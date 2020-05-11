from typing import Callable, List, Tuple
import tempfile

import pandas as pd  # type: ignore

from rider.files import dataprep
from rider.vehicles import get_summaries, wrap_vehicle_type
from rider.routes import get_trips_and_routes, trips_dataframe
from rider.search import default_search
from rider.dataframe import pairs_dataframe

DF = pd.DataFrame

__all__ = [
    "get_dataset",
    "make_subset",
    "make_subset_from_files",
    "default_results",
    "default_pipeline",
]


def read_dataframe(filename, **kwargs):
    def _date(df):
        return df.time.apply(lambda x: pd.Timestamp(x, unit="s").date().__str__())

    print("Reading dataset from local file...")
    df_full = pd.read_csv(filename, usecols=["car", "time", "lat", "lon"], **kwargs)
    print("Adding <date> column...")
    df_full["date"] = _date(df_full)
    return df_full[["car", "date", "time", "lat", "lon"]]


def get_dataset(url: str, folder=None)-> Tuple[DF,DF]:
    """
    Получить основные переменные из данных по адресу *url*.
    Если путь *folder* указан, файлы будут сохранены и переиспользоваться.
    Если путь *folder* не указан, будет использован временный каталог.
    """

    def _get_dataset(url, folder):
        full_csv, summaries_csv = dataprep(url, folder)
        return read_dataframe(full_csv), get_summaries(summaries_csv)

    if folder:
        return _get_dataset(url, folder)
    else:
        with tempfile.TemporaryDirectory() as tmpdirname:
            return _get_dataset(url, tmpdirname)


def make_subset(
    df_full: pd.DataFrame,
    df_summaries: pd.DataFrame,
    days: List[str] = [],
    types: List[str] = [],
):
    def _subset_by_dates(df: pd.DataFrame, days: List[str]) -> pd.DataFrame:
        ix = df.date.isin(days)
        return df[ix]

    def _subset_by_vehicle_types(
        df: pd.DataFrame, types: List[str], resolver: Callable
    ) -> pd.DataFrame:
        ix = df.car.apply(resolver).isin(types)
        return df[ix]

    print("Creating a subset...")
    subset_df = df_full.copy()
    if days:
        subset_df = _subset_by_dates(subset_df, days)
    if types:
        f_ = wrap_vehicle_type(df_summaries)
        subset_df = _subset_by_vehicle_types(subset_df, types, f_)
    print("Done")
    return subset_df


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
    df_full = read_dataframe(full_csv)
    df_summaries = pd.read_csv(summaries_csv)
    df = make_subset(df_full, df_summaries, days, types)
    return default_results(df, limit)
