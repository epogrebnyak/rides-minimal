"""Find vehicle type."""

from typing import List, Callable

import pandas as pd  # type: ignore

__all__ = ["list_types", "get_summaries", "wrap_vehicle_type"]


def list_types() -> List:
    """Перечислить типы автомобилей."""
    return ["bus", "freight", "passenger", "special"]


def vehicle_type_dataframe(cars: pd.DataFrame):
    """Разобрать машины по типам:
       - bus        
       - passenger
       - freight
       - special
    """

    def has(string):
        return lambda s: string in s

    cars["type"] = "other"
    # bus
    cars.loc[cars.car_passengers >= 8, "type"] = "bus"
    # passenger
    ax = (cars.category == "Специальный\\Автобус ") & (cars.type == "other")
    bx = cars.category.apply(has("Легковой")) & (cars.type == "other")
    cars.loc[(ax | bx), "type"] = "passenger"
    # freight
    ix = cars.category.apply(has("Грузовой"))
    cars.loc[ix, "type"] = "freight"
    # special
    ax = cars.category.apply(has("Специальный")) & (cars.type == "other")
    bx = cars.category == "Строительный\\Автокран"
    cars.loc[(ax | bx), "type"] = "special"
    assert len(cars[cars.type == "other"].category.unique()) == 0
    return cars.type


def get_summaries(filename):
    print("Reading summaries from local file...")
    return pd.read_csv(filename)


def wrap_vehicle_type(df: pd.DataFrame) -> Callable:
    """
    Вернуть функцию, которая по идентификатору автомобиля
    будет определять его тип.
    Функция создается на основе данных из файла *filename*. 
    """
    vehicles = df.groupby("car_id").first()

    def vtype(car_id: str):
        return vehicles.loc[car_id]

    return vtype
