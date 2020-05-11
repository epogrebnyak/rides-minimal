"""Find vehicle type."""

from typing import List, Callable

import pandas as pd  # type: ignore

__all__ = ["get_summaries", "CarSummary"]


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


class CarSummary:
    def __init__(self, df: pd.DataFrame):
        self._df = df.groupby("car_id").first()
        from rider.vehicles import vehicle_type_dataframe

        self._src = vehicle_type_dataframe(self._df)

    def category(self, car_id: str):
        return self._df.loc[car_id].category

    def type(self, car_id: str):
        return self._src[car_id]


# x = "eea6db41-360c-11e5-989b-00155d630038"
# car_category(df_summaries, x), car_type(df_summaries, x)
# cs = CarSummary(df_summaries)
# cs.category(x), cs.type(x)

# def wrap_vehicle_type(summary_df: pd.DataFrame) -> Callable:
#     """
#     Вернуть функцию, которая по идентификатору автомобиля
#     будет определять его тип.
#     """
#     vehicles = summary_df.groupby("car_id").first()

#     def vtype(car_id: str):
#         return vehicles.loc[car_id]

#     return vtype
