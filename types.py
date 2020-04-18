"""Расчет попарных характеристик для выборки поездок.

Исходные данные - выборка поездок:

  [Trip]
  
Результат - список словарей, характеризующих пары треков, пример:
    
  {'track_1': 0,
   'track_2': 7,
   'min_dist': 0.132,
   'max_dist': 85.604,
   'cov_1': 0.77,
   'cov_2': 0.26}

'track_1' и 'track_2' - номеры треков из выборки.

'min_dist' и 'max_dist' - расстояния:
             минимальное и максимальное расстояние между фигурами 
             треков.

'cov_1' и 'cov_2' - перекрытие:
             часть трека, которая находится на расстоянии не более
             заданного радиуса от любой точки другого трека в паре 
             сравнения.

"""
import datetime
from dataclasses import dataclass
from typing import List, Tuple, Generator, Callable

import pandas as pd
import numpy as np

from geopy.distance import great_circle
from scipy.spatial.distance import cdist


pd.set_option("mode.chained_assignment", None)


class Route(pd.DataFrame):
    pass


@dataclass
class Trip:
    car_id: str
    date: datetime.date
    route: pd.DataFrame


def get_combinations(n: int) -> List[Tuple[int, int]]:
    from itertools import combinations

    return [(i, j) for i, j in combinations(range(n), 2)]


def count_combinations(n: int) -> int:
    return len(list(get_combinations(n)))


# Импорт данных


def check_incoming_dataframe(df: pd.DataFrame):
    required_columns = set(["car", "lat", "lon", "time"])
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing from {df.head()}: {missing_columns}")


def yield_trips(df: pd.DataFrame) -> Generator[Trip, None, None]:
    check_incoming_dataframe(df)
    df["date"] = df["time"].apply(lambda x: x.date())
    for date in df.date.unique():
        for car in df.car.unique():
            ix = (df.car == car) & (df.date == date)
            yield Trip(car, date, route(df[ix]))


# Работа с треком


def route(df: pd.DataFrame) -> Route:
    res = df[["time"]]
    res["coord"] = list(zip(df.lat, df.lon))
    return res.sort_values("time")


def seconds(series: pd.Series) -> pd.Series:
    return series.apply(lambda x: x.total_seconds())


def duration(df: pd.DataFrame) -> pd.DataFrame:
    return seconds(df.time - df.time.iloc[0]) / 60


def time_deltas(df: pd.DataFrame) -> pd.DataFrame:
    return seconds(df.time.diff())


def dist_delta(df: pd.DataFrame) -> pd.DataFrame:
    df["prev_coord"] = df["coord"].shift(1)
    return df.apply(lambda x: safe_distance(x.coord, x.prev_coord), axis=1)


def milage(df: pd.DataFrame) -> pd.DataFrame:
    return dist_delta(df).cumsum().fillna(0)


def points(route_df: Route) -> np.ndarray:
    return np.array(route_df.coord.to_list())


# Функции расстояний


def distance_km(a: tuple, b: tuple):
    # great_circle() менее точен, но быстрее чем geopy.distance.distance
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


# Функции для апроксимации трека:
#  - [x] по времени в пути (инкремент, количество сегментов)
#  - [x] по расстоянию (инкремент, количество сегментов)
#  - [ ] по астрономическому времени (есть в ноутбке)
#  - [ ] по остановкам (есть в "тяжелом" алгоритме)


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


def time_increment(minutes):
    def accept(route_df):
        xs = duration(route_df)
        ix = growing_index(xs, minutes)
        return route_df.iloc[ix]

    return accept


def distance_increment(km):
    def accept(route_df):
        xs = milage(route_df)
        ix = growing_index(xs, km)
        return route_df.iloc[ix]

    return accept


def find_index_quantile(xs, q):
    if q == 0:
        return 0
    if q == 1:
        return -1
    return np.searchsorted(xs, v=np.quantile(xs, q), side="left")


def find_index(xs, n_segments):
    qs = np.linspace(0, 1, n_segments + 1)
    return [find_index_quantile(xs, q) for q in qs]


def n_segments_by_distance(n):
    def accept(route_df):
        xs = milage(route_df)
        ix = find_index(xs, n)
        return route_df.iloc[ix]

    return accept


def n_segments_by_time(n):
    def accept(route_df):
        xs = duration(route_df)
        ix = find_index(xs, n)
        return route_df.iloc[ix]

    return accept


# Матрица расстояний между точками двух треков


def proximity(r1, r2):
    mat = cdist(points(r1), points(r2), safe_distance_2)
    return Proximity(mat)


@dataclass
class Proximity:
    """Матрица расстояний между двумя треками."""

    mat: np.ndarray

    def min(self):
        """
    Минимиальное расстояние между всеми точками двух треков.
    """
        return round(np.nanmin(self.mat), 3)

    def max(self):
        """
    Максимальное расстояние между всеми точками двух треков.
    """
        return round(np.amax(self.mat), 3)

    def side_min(self, axis: int):
        # 1 is to search by columns - applies to searching minima for 1st route
        # 0 is to search by rows - applies to searching minima for 2nd route
        x = np.nanmin(self.mat, axis)
        return x[~np.isnan(x)]

    def minimal_distances(self):
        return Coverage(self.side_min(1)), Coverage(self.side_min(0))


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
        return round(len(self.in_proximity(radius)) / len(self.mins), 2)


@dataclass
class Examiner:
    approximate_with: Callable
    radius_km: float


def search(
    trips,
    initial=Examiner(n_segments_by_distance(n=10), radius_km=5),
    refined=Examiner(distance_increment(km=2.5), radius_km=2.5*1.2),
    limit=None,
):

    f = initial.approximate_with
    g = refined.approximate_with
    radius_1 = initial.radius_km
    radius_2 = refined.radius_km

    m = len(trips)
    count = count_combinations(m)
    print(f"{count} pairs are possible for {m} tracks")

    # Грубая апроксимация треков
    routes = [f(t.route) for t in trips]
    print(f"Simplified {len(trips)} routes")

    def prox(tup: tuple):  # замыкание для доступа к routes
        i, j = tup
        return proximity(routes[i], routes[j])

    # Выбор пересекающися пар
    pairs = [p for p in get_combinations(len(trips)) if prox(p).min() < radius_1]
    print(f"Found {len(pairs)} pairs of intersecting routes")
    print("Refining approximation for intersected routes...")

    # Урезаем для демо-примеров
    if limit:
        pairs = pairs[0:limit]
        print(f"Trimmed dataset to {limit} pairs")

    # Уточняем апроксимацию треков
    from itertools import chain

    for k, i in enumerate(set(chain.from_iterable(pairs))):
        routes[i] = g(trips[i].route)
    print(f"Made better approximation of {k} routes")
    print("Calculating distances between routes and reporting...")

    # Считаем перекрытие треков в пересекающися парах

    for (i, j) in pairs:
        p = proximity(routes[i], routes[j])
        if p.min() < radius_1:
            md1, md2 = p.minimal_distances()
            yield dict(
                track_1=i,
                track_2=j,
                min_dist=p.min(),
                max_dist=p.max(),
                cov_1=md1.coverage(radius_2),
                cov_2=md2.coverage(radius_2),
            )


if __name__ == "__main__":
    # Получаем данные
    assert len(get_combinations(49)) == 1176

    def get_dataframe():
        return pd.read_csv("one_day.zip", parse_dates=["time"])

    df = get_dataframe()
    assert df.shape == (131842, 6)
    print("Finished reading data from file")

    trips = list(yield_trips(df))
    assert len(trips) == 49
    print(f"Created list of {len(trips)} trips")

    # Запускаем алгоритм
    results_ = list(search(trips, limit=None))

    results = (
        pd.DataFrame(results_)
        .assign(cov_total=lambda r: r.cov_1 + r.cov_2)
        .sort_values("cov_total", ascending=False)
        .reset_index(drop=True)
        .head(10)
    )
    print(results)
    results.to_csv("output.csv", index=None)

    """        
    План перенести из ноутбука
    -------------------------
    
    Визуализация:          
        
      - [ ] отрисовка треков на карте     
      - [ ] прочие
       
    Фильтры:        
        
      - [ ] по направлению
      - [ ] по времени         
      
    Соображения
    -----------
    
    - в функциях упрощения много повторов кода, можно рефакторить
    - для пробега нам нужно перезапускть duration() - много расчетов 
    
    """
