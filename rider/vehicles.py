import pandas as pd  # type: ignore


def types():
    return {"bus", "freight", "passenger", "special"}


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


def all_cars(filename):
    return pd.read_csv(filename).groupby("car_id").first()


def wrap_vehicle_type(filename):
    vehicles = vehicle_type_dataframe(all_cars(filename))

    def vtype(car_id: str):
        return vehicles.loc[car_id]

    return vtype
