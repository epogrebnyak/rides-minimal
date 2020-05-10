from dataclasses import dataclass
from typing import List, Callable

import pandas as pd
import numpy as np

pd.set_option("mode.chained_assignment", None)

from .helpers import safe_distance


@dataclass
class Trip:
    car: str
    date: str


class Route(pd.DataFrame):
    pass

    @property
    def milage(self):
        return milage(self)


def slices(df: pd.DataFrame):
    for k, v in df.groupby(["car", "date"]):
        yield Trip(*k), make_route(v)


def get_trips_and_routes(df: pd.DataFrame) -> (List[Trip], List[Route]):
    trips = []
    routes = []
    for (t, r) in slices(df):
        trips.append(t)
        routes.append(r)
    return trips, routes


def coord(df: pd.DataFrame):
    return list(zip(df.lat, df.lon))


def make_route(df: pd.DataFrame) -> Route:
    res = df[["time", "lat", "lon"]]
    res["coord"] = coord(df)
    return Route(res.sort_values("time"))


def trip_dicts(trips, routes, milages):
    for t, r, m in zip(trips, routes, milages):
        yield dict(car=t.car, start=start_time(r), end=end_time(r), km=m)


def trips_dataframe(trips, routes, milages):
    return pd.DataFrame(trip_dicts(trips, routes, milages))


def duration_acc(df: pd.DataFrame) -> pd.DataFrame:
    return (df.time - df.time.iloc[0]) / 60


def time_deltas(df: pd.DataFrame) -> pd.DataFrame:
    return df.time.diff()


def distance_deltas(df: pd.DataFrame) -> pd.DataFrame:
    res = df.copy()
    res["prev_coord"] = res.coord.shift(1)
    return res.apply(lambda x: safe_distance(x.coord, x.prev_coord), axis=1)


def milage_acc(df: pd.DataFrame) -> pd.DataFrame:
    return distance_deltas(df).cumsum().fillna(0)


def milage(route) -> float:
    return round(milage_acc(route).iloc[-1], 2)


def points(route_df: Route) -> np.ndarray:
    return np.array(route_df.coord.to_list())


def date(route):
    return route.iloc[0].time.date()


def timestamp(x):
    return pd.Timestamp(x, unit="s")


def nth_timestamp(route, n):
    return timestamp(route.iloc[n].time)


def start_time(route):
    return nth_timestamp(route, 0)


def end_time(route):
    return nth_timestamp(route, -1)


def true_quantile(xs, q):
    """Квантиль накопленной суммы списка xs без учета повторов. 
     
     np.quantile дает неправильный для нас результат:
     np.quantile(xs, 0.9) может быть равно len(xs),
     если в хвосте xs много повторов.
  """
    assert 0 <= q <= 1
    end_value = xs[-1] * q
    is_smaller = lambda x: 1 if x <= end_value else 0
    return sum(map(is_smaller, xs))


def where(xs, q):
    i = true_quantile(xs, q)
    return np.searchsorted(xs, xs[i], side="left")


def find_index_one(xs: List, q: float) -> int:
    """Перестраховываемся по сравнению с where."""
    if q == 0:
        return 0
    if q == 1:
        return -1
    return where(xs, q)


def find_index(xs: List, n_segments: int) -> List[int]:
    qs = np.linspace(0, 1, n_segments + 1)
    return [find_index_one(xs, q) for q in qs]


def n_segments_by(n: int, route: Route, acc_with: Callable):
    xs = acc_with(route).tolist()
    ix = find_index(xs, n)
    return route.iloc[ix]


def n_segments_by_distance(n: int):
    return lambda route: n_segments_by(n, route, milage_acc)


def n_segments_by_time(n: int):
    return lambda route: n_segments_by(n, route, duration_acc)


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


def time_increment(minutes: int):
    def accept(route: Route):
        xs = duration_acc(route)
        ix = growing_index(xs, minutes)
        return route.iloc[ix]

    return accept


def distance_increment(step_km: float):
    def accept(route: Route):
        xs = milage_acc(route)
        ix = growing_index(xs, step_km)
        return route.iloc[ix]

    return accept
