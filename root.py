import pandas as pd

# Исходные данные, один день поездок всех типов транспорта
# Гарантированы колонки:     'time', 'lon', 'lat', 'car', 'ride', 'type'
# Даны или рассчитываются:   'dist', 'time_delta'

# Ход решения:

# 1. Определить, что анализируем?
#   1.1 сделать выборку поездок (например, только грузовые)
#   1.2 перевести датафрейм в список треков
#   1.3 создать список пар треков
# 2. Выкинуть пары треков, которые не пересекаются
# 3. Для оставшихся пар треков оценить степень их сближения по широким критериям
# 4. Сгруппировать треки или ужесточить критерии сходимости
# 5. Представить результаты с акцентом на дальнейшее применение в бизнесе
#    (уменьшение пробега с сохранением расписания доставки)

"""Преобразования типов:
    
Trip = pd.Dataframe
    
pd.Dataframe -> [Trip] -> (Trip->Trip) -> [(int, int), float] -> float ->
             -> [(int, int)] -> 
             -> (Trip->Trip) -> [(int, int), (float, float)] 
             
(int -> str)
"""

# Компоненты решения:
# - функции для апроксимации треков
#   - равные расстояния
#   - доля пробега
#   - по времени
#    -c остановками
# - матрица дистанций между точками двух треков, метрики близости, маска оценки только диагонали
# - оценка близости треков

# Визуализация:
# - отрисовка треков на карте

from typing import List

Trip = pd.DataFrame
Sample = List[Trip]


def combinations(trips: List[Trip]):
    from itertools import combinations
    ix = range(len(trips))
    return list(combinations(ix, 2))


def reduce_with(trips: List[Trip], func):
    return [func(t) for t in trips]


def make_trip_list(df: pd.DataFrame) -> List[Trip]:
    trips = []
    for date in df.date.unique():
        for car in df.car.unique():
            ix = (df.car == car) & (df.date == date)
            trip = df[ix]
            trips.append(trip)
    return [strip(t) for t in trips]


def strip(t: pd.DataFrame) -> Trip:
    """
    Приведение данных о треке в стандартный вид.
    Расчет дополнительных колонок.
    """
    required_columns = ["car", "date", "lat", "lon", "time", "dist", "time_delta"]
    available_columns = t.columns
    for col in required_columns:
        assert col in available_columns
    res = t[["time", "lon", "lat", "date", "car"]]
    res["time"] = t.time.apply(lambda x: x.time())
    res["milage"] = t.dist.cumsum()
    res["duration"] = t.time_delta.cumsum() / (60 * 60)
    return res

# NEXT:
# from vectors import growing_index, percentile_index, qs

# def equidist(t, step_km):
#   """Взять равные промежутки по *step_km* расстояния."""
#   ix = growing_index(t.milage, step_km)
#   return t.iloc[ix,:]

# def spaced_dist(t, n: int, start=False, end=False):
#   """Взять *n* равных промежутков по расстоянию.
#   Опционально исключить начало и конец трека.
#   """
#   ix = percentile_index(t.milage, qs(n, start, end))
#   return t.iloc[ix,:]

pd.options.mode.chained_assignment = None
df = pd.read_csv("one_day.zip", parse_dates=["time", "date"], nrows=100_000)
raw_trips = make_trip_list(df)
assert len(raw_trips) == 38
reduced_trips = reduce_with(raw_trips, lambda t: t.iloc[-1].milage)
assert round(reduced_trips[0], 2) == 266.04
all_pairs = combinations(raw_trips)
assert len(all_pairs) == 38 * 37 /2
