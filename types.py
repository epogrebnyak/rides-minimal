from dataclasses import dataclass

# точки трека внутри суток
Route = pd.Dataframe

@dataclass
class Trip:
  car_id: str
  date: datetime.date
  route: Route

Float = Union[Float, None].

@dataclass
class Pair:
  i: int
  j: int
  max_dist: 
  
   


# Исходные данные алгоритма: [Trip]
# Результат [(i, j, p1, p2)] -> (i, j, p1+p2)
