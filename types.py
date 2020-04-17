"""Расчет попарных характеристик для выборки поездок.

Исходные данные - выборка поездок:

  [Trip]
  
Результат - набор характеристик Leash (два числа) и 
            Coverage (два числа) для каждой пары Pair:
    
  [(Pair, Leash, Coverage)]
  
он же:

  [(int, int), (float, float), (float, float)]  

"""
import datetime
from dataclasses import dataclass

import pandas as pd
import numpy as np

from geopy.distance import great_circle

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


@dataclass
class Pair:
    """Номера треков в паре."""

    i: int
    j: int


@dataclass
class Leash:
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


def combinations(n: int) -> [Pair]:
    from itertools import combinations

    return [Pair(i, j) for i, j in combinations(range(n), 2)]


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
    r = df[["time", "lat", "lon"]]
    r["time"] = df.time.apply(lambda x: x.time())
    return r.sort_values("time")


def duration(df: pd.DataFrame) -> pd.DataFrame:
    df["time_delta"] = df.time.diff().apply(lambda x: x.total_seconds())
    return df["time_delta"].cumsum() / (60 * 60)


def milage(df: pd.DataFrame) -> pd.DataFrame:
    df["coord"] = list(zip(df.lat, df.lon))
    df["dist_delta"] = dist_delta(df)
    return df["dist_delta"].cumsum()


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


df = get_dataframe()
assert df.shape == (131842, 6)
assert set(df.columns.to_list()) == set(["car", "ride", "time", "lon", "lat", "type"])
print("route")
trips = list(yield_trips(df))
assert len(trips) == 49 
