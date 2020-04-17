"""Расчет попарных характеристик для выборки поездок.

Исходные данные - выборка поездок:

  [Trip]
  
Результат - набор характеристик Leash (два числа) и 
            Coverage (два числа) для каждой пары Pair:
    
  [(Pair, Distances, Coverage)]
  
он же:

  [(int, int), (float, float), (float, float)]  

"""
import datetime
from dataclasses import dataclass

import pandas as pd
import numpy as np

from geopy.distance import great_circle
from scipy.spatial.distance import cdist

pd.set_option("mode.chained_assignment", None)


class Route(pd.DataFrame):
    """    
    Точки трека машины внутри одних суток.
    Отсортированы по возрастанию времени.   
    """

    pass


@dataclass
class Trip:
    car_id: str
    date: datetime.date
    route: pd.DataFrame


# @dataclass
# class Pair:
#     """Номера треков в паре."""

#     i: int
#     j: int


@dataclass
class Distances:
    """Минимальная и максимальная дистанция между фигурами треков."""

    min: float
    max: float


@dataclass
class Coverage:
    """Перекрытие треков в паре:
      
      left_by_right - какая часть первого трека 
                      перекрыта вторым треком, 
                      число от 0 до 1.
      
      right_by_left - какая часть второго трека 
                      перекрыта первым треком, 
                      число от 0 до 1.      
  """

    left_by_right: float
    right_by_left: float


def combinations(n: int) -> (int, int):
    from itertools import combinations

    return [(i, j) for i, j in combinations(range(n), 2)]


assert len(combinations(49)) == 1176


def get_dataframe():
    return pd.read_csv("one_day.zip", parse_dates=["time"])


def yield_trips(df: pd.DataFrame) -> [Trip]:
    df["date"] = df["time"].apply(lambda x: x.date())
    for date in df.date.unique():
        for car in df.car.unique():
            ix = (df.car == car) & (df.date == date)
            yield Trip(car, date, route(df[ix]))


def route(df: pd.DataFrame) -> pd.DataFrame:
    res = df[["time"]]
    res['coord'] = list(zip(df.lat, df.lon))    
    return res.sort_values("time")


def seconds(series):
    return series.apply(lambda x: x.total_seconds())


def duration(df: pd.DataFrame) -> pd.DataFrame:
    return seconds(df.time - df.time.iloc[0]) / 60 


def time_deltas(df: pd.DataFrame) -> pd.DataFrame:
    return seconds(df.time.diff())


def milage(df: pd.DataFrame) -> pd.DataFrame:
    return dist_delta(df).cumsum()


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
    result = [0] # will include start point
    current = xs[0]
    for i, x in enumerate(xs):
        accumulated = x - current
        if accumulated >= step:
            result.append(i)
            accumulated = 0
            current = x
    n = len(xs)-1        
    if result[-1] != n: # will include end point
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


def get_distances(r1, r2):
    return Proximity(cdist(points(r1), points(r2), safe_distance_2))

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


def simplify1(route_df):
    return distance_step(time_step(route_df, 30), 10)

def simplify2(route_df):
    return distance_step(route_df, 5)
    

df = get_dataframe()
assert df.shape == (131842, 6)
assert set(df.columns.to_list()) == set(["car", "ride", "time", "lon", "lat", "type"])
print("Finished reading data from file")
trips = list(yield_trips(df))
assert len(trips) == 49
print("Created list of trips")

routes = [simplify1(t.route) for t in trips]
print("Simplified routes")

  
prox1 = [(i, j, get_distances(routes[i], routes[j])) 
         for i,j in combinations(len(trips))]

pairs = [(i,j) for (i, j, p) in prox1 if p.min() < 5]
assert len(pairs) == 375
print("Found cadidate pairs")

#TODO: calculate for overlap for pairs in in Proximity class

ns = set([x for xs in pairs for x in xs])
for n in ns:
    routes[n] = simplify2(trips[n].route)
print("Made better approximation of pairs")


prox2 = [(i, j, get_distances(routes[i], routes[j])) 
         for i,j in pairs]

for (i,j, p) in prox2:
    print(i,j, p.min())

def side_min(mat, axis):
  x = np.nanmin(mat, axis)
  return x[~np.isnan(x)]