from typing import Callable, List

import pandas as pd  # type: ignore

from .files import dataprep
from .vehicles import wrap_vehicle_type
from .routes import get_trips_and_routes, trips_dataframe
from .search import default_search
from .dataframe import pairs_dataframe


def _get_date(df):
    return df.time.apply(lambda x: pd.Timestamp(x, unit="s").date().__str__())


def read_dataframe(filename, **kwargs):
    df_full = pd.read_csv(filename, usecols=["car", "time", "lat", "lon"], **kwargs)
    df_full["date"] = _get_date(df_full)
    return df_full[["car", "date", "time", "lat", "lon"]]


def get_dataset(url, folder):
    full_csv, summaries_csv = dataprep(url, folder)
    return read_dataframe(full_csv), wrap_vehicle_type(summaries_csv)


def get_dataset0(url: str):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        return get_dataset(url, tmpdirname)


def _subset_by_dates(df: pd.DataFrame, days: List[str]) -> pd.DataFrame:
    ix = df.date.isin(days)
    return df[ix]


def _subset_by_vehicle_types(
    df: pd.DataFrame, types: List[str], resolver: Callable
) -> pd.DataFrame:
    ix = df.car.apply(resolver).isin(types)
    return df[ix]


def make_subset(
    df_full: pd.DataFrame,
    vehicle_type: Callable,
    days: List[str] = [],
    types: List[str] = [],
):
    print("Creating a sunset of data...")
    subset_df = df_full.copy()
    if days:
        subset_df = _subset_by_dates(subset_df, days)
    if types:
        subset_df = _subset_by_vehicle_types(subset_df, types, vehicle_type)
    print("Done")    
    return subset_df


def make_subset_from_files(full_csv, summaries_csv, days, types):
    return make_subset(
        read_dataframe(full_csv), wrap_vehicle_type(summaries_csv), days, types
    )


def default_results(df, limit=None):
    print("Extracting list of routes...")    
    trips, routes = get_trips_and_routes(df)
    print("Calcultaing route length...")
    milages = [r.milage for r in routes]
    print("Entering proximity search...")
    result_dicts = default_search(routes, limit)
    print("Reporting...")
    pairs_df = pairs_dataframe(result_dicts, milages)
    trips_df = trips_dataframe(trips, routes, milages)
    return (trips_df, pairs_df), (trips, routes, milages)


def default_pipeline(url, data_folder, days=[], types=[], limit: int = None):
    full_csv, summaries_csv = dataprep(url, data_folder)
    df = make_subset_from_files(full_csv, summaries_csv, days, types)
    return default_results(df, limit)
