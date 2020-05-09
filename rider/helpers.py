from typing import Tuple, Callable
import numpy as np
from geopy.distance import great_circle


def distance_km(a: tuple, b: tuple):
    # great_circle() менее точен, но быстрее чем geopy.distance.distance
    # https://geopy.readthedocs.io/en/stable/#module-geopy.distance
    return great_circle(a, b).km


Coord = Tuple[float, float]

# используется с distance_delta
def safe_distance(a: Coord, b: Coord) -> float:
    # if not isinstance(b, tuple): # catch NaN
    #  return 0
    if a == b:
        return 0
    try:
        return distance_km(a, b)
    except ValueError:
        return np.nan


# используется с cdist
def safe_distance_2(a: Coord, b: Coord) -> float:
    x1, y1 = a
    x2, y2 = b
    if np.isnan(x1) or np.isnan(x2):
        return np.nan
    else:
        return round(distance_km(a, b), 9)


def from_cache(filename: str, getter: Callable):
    """Прочитать объект из *filename* или
     создать объект с помощью getter и сохранить 
     его в *filename*.
     Возвращает значение getter().
  """
    import json, os

    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        content = getter()
        with open(filename, "w") as f:
            json.dump(content, f)
        return content
