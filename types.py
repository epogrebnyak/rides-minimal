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
import pandas as pd
from dataclasses import dataclass

class Route(pd.DataFrame):
    """    
    Точки трека машины внутри одних суток.
    Отсортированы по возрастанию времени.   
    
    Колонки:                 
        (lat, lon): (float, float) - широта и долгота точки трека
        time: datetime.time() - время регистрации точки трека
        duration: float - накопленное время с начала поездки
        milage: float - пробег с начала поездки
    """
    pass

@dataclass
class Trip:
  car_id: str
  date: datetime.date
  route: Route

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
    return [Pair(i, j) for i,j in combinations(range(n), 2)]

assert len(combinations(49)) == 1176

def get_dataframe():
  return pd.read_csv("one_day.zip", parse_dates=["time_stamp"])

df = get_dataframe()
assert df.shape == (216757, 4)

# TODO: df -> [Trips] 
#  - посчитать дельты расстояний и времени
#  - аккумулировать их в milage и duration


