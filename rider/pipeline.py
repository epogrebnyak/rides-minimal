from typing import Callable, List, Tuple
import tempfile

import pandas as pd  # type: ignore

from rider.files import dataprep
from rider.vehicles import get_summaries, CarSummary
from rider.routes import get_trips_and_routes
from rider.search import default_search
from rider.dataframe import pairs_dataframe, trips_dataframe


__all__ = [
    "get_dataset",
    "make_subset",
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


def get_dataset(url: str, folder=None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Получить основные переменные из данных по адресу *url*.
    Если путь *folder* указан, файлы будут сохранены и переиспользоваться.
    Если путь *folder* не указан, будет использован временный каталог.
    """

    def from_folder(url, folder):
        full_csv, summaries_csv = dataprep(url, folder)
        return read_dataframe(full_csv), get_summaries(summaries_csv)

    if folder:
        return from_folder(url, folder)
    else:
        with tempfile.TemporaryDirectory() as tmpdirname:
            return from_folder(url, tmpdirname)


def make_subset(
    df_full: pd.DataFrame,
    df_summaries: pd.DataFrame,
    days: List[str] = [],
    types: List[str] = [],
):
    print("Creating a subset...")
    subset_df = df_full.copy()
    if days:
        ix = subset_df.date.isin(days)
        subset_df = subset_df[ix]
    if types:
        cs = CarSummary(df_summaries)
        ix = subset_df.car.apply(cs.type).isin(types)
        subset_df = subset_df[ix]
    print("Done")
    return subset_df


def default_results(data_df, summary_df, limit=None):
    print("Extracting list of routes...")
    trips, routes = get_trips_and_routes(data_df)
    print("Calcultaing route length...")
    milages = [r.milage for r in routes]
    print("Entering proximity search...")
    result_dicts = default_search(routes, limit)
    print("Reporting pairs...")
    pairs_df = pairs_dataframe(result_dicts, milages)
    print("Reporting individual routes...")
    trips_df = trips_dataframe(trips, routes, milages, summary_df)
    return (trips_df, pairs_df), (trips, routes, milages)


def default_pipeline(url, data_folder, days=[], types=[], limit: int = None):
    full_csv, summaries_csv = dataprep(url, data_folder)
    df_full = read_dataframe(full_csv)
    df_summaries = pd.read_csv(summaries_csv)
    df = make_subset(df_full, df_summaries, days, types)
    return default_results(df, df_summaries, limit)
