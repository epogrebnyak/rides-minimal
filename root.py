"""
Задача
======

По данным маршрутов поездок корпоративного автопарка выявить 
дублирование (сходимость) поездок.


Ход решения
===========

1. Определить выборку, которую анализируем
   1.1 сделать выборку на уровне датафрейма (например, только грузовые)
   1.2 перевести датафрейм в список треков
   1.3 создать список пар треков
2. Выкинуть пары треков, которые не пересекаются
3. Для оставшихся пар треков оценить степень их сближения по широким критериям
4. Сгруппировать треки или ужесточить критерии сходимости
5. Представить результаты с акцентом на дальнейшее применение в бизнесе
   (цель - уменьшение пробега с сохранением расписания доставки).

Преобразования типов
====================
  
1. Создание выборки треков   
Trip = pd.Dataframe
pd.Dataframe -> [Trip]

2. Выбраковка непересекающися пар треков
[Trip] -> (Trip->Trip) -> [(int, int), float] -> float -> [(int, int)]

3. Анализ сходимости пересекащихся пар треков
[Trip] -> (Trip->Trip) -> [(int, int)] -> [(int, int), (float, float)] 

Компоненты решения
==================

    
Матрица дистанций между точками двух треков, метрики близости, маска оценки только диагонали

Оценка близости треков


Визуализация
============

- отрисовка треков на карте

"""

import pandas as pd


from typing import List

Trip = pd.DataFrame


def combinations(trips: List[Trip]) -> [(int, int)]:
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
            trip = df[ix].sort_values("time", ascending=True)
            trips.append(trip)
    return [strip(t) for t in trips]


def check_incoming_dataframe(df: pd.DataFrame):
    # Исходные данные:        ['time', 'lon', 'lat', 'car', 'ride', 'type']
    # Должны быть посчитаны:  ['dist', 'time_delta']
    required_columns = ["car", "date", "lat", "lon", "time", "dist", "time_delta"]
    available_columns = df.columns
    for col in required_columns:
        if col not in available_columns:
            raise ValueError(f"Column {col} missing from {df.head()}")


def strip(t: pd.DataFrame) -> Trip:
    """
    Приведение данных о треке в стандартный вид.
    Расчет дополнительных колонок.
    """
    check_incoming_dataframe(t)
    res = t[["time", "lon", "lat", "date", "car"]]
    res["time"] = t.time.apply(lambda x: x.time())
    res["milage"] = t.dist.cumsum()
    res["duration"] = t.time_delta.cumsum() / (60 * 60)
    return res


# NEXT: drop in vectors.py
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
assert raw_trips[0].time.iloc[0] < raw_trips[0].time.iloc[-1]
reduced_trips = reduce_with(raw_trips, lambda t: t.iloc[-1].milage)
assert round(reduced_trips[0], 2) == 266.04
all_pairs = combinations(raw_trips)
assert len(all_pairs) == 38 * 37 / 2
