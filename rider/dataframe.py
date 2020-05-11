"""Representaion of results as dataframes."""

from typing import List
import pandas as pd  # type: ignore

from rider.vehicles import CarSummary

__all__ = ["pairs_dataframe", "trips_dataframe"]


def overlap(df):
    return (
        (df.cov_1 * df.len_1 + df.cov_2 * df.len_2).divide(df.len_1 + df.len_2).round(2)
    )


def extend(df, milages):
    km = lambda i: milages[i]
    df["cov"] = df.cov_1 + df.cov_2
    df["len_1"] = df.id_1.apply(km)
    df["len_2"] = df.id_2.apply(km)
    df['len'] = df["len_1"] + df["len_2"]
    df["op"] = overlap(df)
    return df


def pairs_dataframe(dicts: List[dict], milages: List[float]):
    """
    Создать датафрейм с парными характеристиками поездок.    
    """
    df = pd.DataFrame(dicts)
    df = extend(df, milages)
    return df.sort_values("cov", ascending=False).reset_index(drop=True)


def trip_dicts(trips, routes, milages, summary_df):
    cs = CarSummary(summary_df)
    for t, r, m in zip(trips, routes, milages):
        yield dict(
            car=t.car,
            type=cs.type(t.car),
            cat=cs.category(t.car),
            start=r.start_time,
            end=r.end_time,
            km=m,
        )


def trips_dataframe(trips, routes, milages, summary_df):
    """
    Создать датафрейм с характеристиками поездок.    
    """
    return pd.DataFrame(trip_dicts(trips, routes, milages, summary_df))
