"""Расчет попарных характеристик для выборки поездок.

Исходные данные - выборка поездок:

  [Trip]
  
Результат - перекрытие треков в паре (два числа от 0 до 1)
    
  [(int, int, float, float)]

Перекрытие - часть трека, которая находится на расстоянии не более
             заданного радиуса от любой точки другого трека в паре 
             сравнения.

"""
import datetime
from dataclasses import dataclass

import pandas as pd
import numpy as np

from geopy.distance import great_circle
from scipy.spatial.distance import cdist

pd.set_option("mode.chained_assignment", None)


@dataclass
class Trip:
    car_id: str
    date: datetime.date
    route: pd.DataFrame


def combinations(n: int) -> (int, int):
    from itertools import combinations

    return [(i, j) for i, j in combinations(range(n), 2)]


assert len(combinations(49)) == 1176


def check_incoming_dataframe(df: pd.DataFrame):
    required_columns = set(["car", "lat", "lon", "time"])
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing from {df.head()}: {missing_columns}")


def yield_trips(df: pd.DataFrame) -> [Trip]:
    check_incoming_dataframe(df)
    df["date"] = df["time"].apply(lambda x: x.date())
    for date in df.date.unique():
        for car in df.car.unique():
            ix = (df.car == car) & (df.date == date)
            yield Trip(car, date, route(df[ix]))


def route(df: pd.DataFrame) -> pd.DataFrame:
    res = df[["time"]]
    res["coord"] = list(zip(df.lat, df.lon))
    return res.sort_values("time")


def seconds(series):
    return series.apply(lambda x: x.total_seconds())


def duration(df: pd.DataFrame) -> pd.DataFrame:
    return seconds(df.time - df.time.iloc[0]) / 60


def time_deltas(df: pd.DataFrame) -> pd.DataFrame:
    return seconds(df.time.diff())


def milage(df: pd.DataFrame) -> pd.DataFrame:
    return dist_delta(df).cumsum().fillna(0)


def dist_delta(df: pd.DataFrame) -> pd.DataFrame:
    df["prev_coord"] = df["coord"].shift(1)
    return df.apply(lambda x: safe_distance(x.coord, x.prev_coord), axis=1)


def distance_km(a: tuple, b: tuple):
    # great_circle - менее точен, но быстрее чем geopy.distance.distance
    # https://geopy.readthedocs.io/en/stable/#module-geopy.distance
    return great_circle(a, b).km


def safe_distance(a, b):
    if a == b:
        return 0
    try:
        return distance_km(a, b)
    except ValueError:
        return np.nan


def safe_distance_2(a, b):
    x1, y1 = a
    x2, y2 = b
    if np.isnan(x1) or np.isnan(x2):
        return np.nan
    else:
        return distance_km(a, b)


def growing_index(xs, step):
    xs = [x for x in xs]
    result = [0]  # will include start point
    current = xs[0]
    for i, x in enumerate(xs):
        accumulated = x - current
        if accumulated >= step:
            result.append(i)
            accumulated = 0
            current = x
    n = len(xs) - 1
    if result[-1] != n:  # will include end point
        result.append(n)
    return result


def time_step(route_df, minutes=60):
    xs = duration(route_df)
    ix = growing_index(xs, minutes)
    return route_df.iloc[ix]


def distance_step(route_df, km=5):
    xs = milage(route_df)
    ix = growing_index(xs, km)
    return route_df.iloc[ix]


def points(route_df) -> np.ndarray:
    return np.array(route_df.coord.to_list())


def proximity(r1, r2):
    mat = cdist(points(r1), points(r2), safe_distance_2)
    return Proximity(mat)


@dataclass
class Coverage:
    """Для каждой точки выбранного трека посчитано 
       минимальное из расстояний до точек другого трека.
       
       Если в треке 10 точек, то минимальных расстояний 
       до другого трека будет 10.
       
       Мы выбираем те из расстояний, которые меньше заданного 
       порога(радиуса) сближения.
              
       Предположим в треке 10 точек и минимальные расстояния до 
       фигуры второго трека такие:
       
       >> mins = [21.2, 22.6, 17.6, 7.7, 2.7, 0.3, 0.4, 0.6, 0.2, 3.1]
       
       Тогда "сблизившимися" с другим треков при радиусе точности 1 
       мы считаем 4 точки:
       
       >> radius = 1           
       >> [x for x in mins if x < radius]
       [0.3, 0.4, 0.6, 0.2]
       
       Коэффциент перекрытия составляет 4/10 = 40%. 
       
       Он показывает, что 40% точек данного трека
       находились на расстоянии не более чем *radius*
       от какой-то точки другого трека.
       
       Замечания:
       
       - Коэффциент перекрытия (КП) может интепретироваться как 
         часть пути, если отрезки между точками равные. 
         
       - Значение коэффциента перекрытия зависит от точности 
         апроксимации трека и радиуса.       
         
       - Треки могут иметь сложную форму, высокий КП не гарантирует,
         что доставку по одному треку можно переложить на другой трек.
         Но при низких КП это заведомо невозможно.
         
       - Нулевой КП - машины ездили в разных местах.  
         
    """

    mins: np.ndarray

    def in_proximity(self, radius: float):
        """Все минимальные расстояния до другого трека, величина 
          которых меньше заданного радиуса сближения.
       """
        return self.mins[self.mins < radius]

    def coverage(self, radius: float):
        """Коэффициент перекрытия - доля трека, которая находится 
           на расстоянии не более заданного радиуса от другого трека.
        """
        return len(self.in_proximity(radius)) / len(self.mins)


@dataclass
class Proximity:
    """Матрица расстояний между двумя треками."""

    mat: np.ndarray

    def min(self):
        """
    Минимиальное расстояние между всеми точками двух треков.
    """
        return np.nanmin(self.mat)

    def max(self):
        """
    Максимальное расстояние между всеми точками двух треков.
    """
        return np.amax(self.mat)

    def side_min(self, axis: int):
        # 1 is to search by columns - applies to searching minima for 1st route
        # 0 is to search by rows - applies to searching minima for 2nd route
        x = np.nanmin(self.mat, axis)
        return x[~np.isnan(x)]

    def minimal_distances(self):
        return Coverage(self.side_min(1)), Coverage(self.side_min(0))


def members(pairs):
    return [p for pair in pairs for p in pair]


def search(
    trips,
    approximate_1=lambda df: time_step(df, minutes=60),
    radius_1=5,
    approximate_2=lambda df: distance_step(df, km=2.5),
    radius_2=2.5 * 1.2,
    limit=None,
):

    # Грубая апроксимация треков
    routes = [approximate_1(t.route) for t in trips]
    print("Simplified routes")

    def prox(tup: tuple):  # замыкание для доступа к routes
        i, j = tup
        return proximity(routes[i], routes[j])

    # Выбор пересекающися пар
    pairs = [p for p in combinations(len(trips)) if prox(p).min() < radius_1]
    print(f"Found {len(pairs)} pairs of intersecting routes")
    print("Refining approximation for candidate routes...")

    # урезаем для демо-примеров
    if limit:
        pairs = pairs[0:limit]

    # Уточняем апроксимацию треков
    for i in members(pairs):
        routes[i] = approximate_2(trips[i].route)
    print(f"Made better approximation of {len(members(pairs))} routes")
    print("Calculating distances between routes and reporting...")

    # Считаем перекрытие треков в пересекающися парах

    for (i, j) in pairs:
        p = proximity(routes[i], routes[j])
        if p.min() < radius_1:
            md1, md2 = p.minimal_distances()
            yield (i, j, p.min(), md1.coverage(radius_2), md2.coverage(radius_2))


def pct(x: float) -> str:
    return f"{x*100:.0f}%"


if __name__ == "__main__":

    def get_dataframe():
        return pd.read_csv("one_day.zip", parse_dates=["time"])

    df = get_dataframe()
    assert df.shape == (131842, 6)
    print("Finished reading data from file")

    trips = list(yield_trips(df))
    assert len(trips) == 49
    print(f"Created list of {len(trips) } trips")

    results = list(search(trips, limit=10))
    for (i, j, m, c1, c2) in results:
        print(i, j, round(m, 2), pct(c1), pct(c2))

    """
    Фукнция раздить на n сегментов по расстоянию, по времени
    
    Функции для апроксимации треков
       - равные расстояния
       - доля пробега
       - по времени
       - c остановками
        
    Визуализация   
       - отрисовка треков на карте     
       
    Фильтры:
        - по направлению
        - по времени        
    """
