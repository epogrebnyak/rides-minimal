import pandas as pd

from rider import (
    DataFolder,
    wrap_vehicle_type,
    get_trips_and_routes,
    default_search,
    trips_dataframe,
    pairs_dataframe,
)


def get_date(df):
    return df.time.apply(lambda x: pd.Timestamp(x, unit="s").date().__str__())


def read_dataframe(filename, **kwargs):
    df_full = pd.read_csv(filename, usecols=["car", "time", "lat", "lon"], **kwargs)
    df_full["date"] = get_date(df_full)
    return df_full[["car", "date", "time", "lat", "lon"]]


def get_dataset(url, folder):
    f = DataFolder(folder)
    f.download(url)
    trackpoints_csv = f.save_trackpoints()
    summaries_csv = f.save_summaries()
    return read_dataframe(trackpoints_csv), wrap_vehicle_type(summaries_csv)


def get_dataset0(url):
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdirname:
        return get_dataset(url, tmpdirname)


def subset_by_dates(df, days: [str]):
    ix = df.date.isin(days)
    return df[ix]


def subset_by_vehicle_types(df, types: [str], vehicle_type_resolver):
    ix = df.car.apply(vehicle_type_resolver).isin(types)
    return df[ix]


def make_subset(full_csv, summaries_csv, days, types):
    subset_df = read_dataframe(full_csv)
    if days:
        subset_df = subset_by_dates(subset_df, days)
    if types:
        vehicle_type = wrap_vehicle_type(summaries_csv)
        subset_df = subset_by_vehicle_types(subset_df, types, vehicle_type)
    return subset_df


def default_results(df, limit=None):
    trips, routes = get_trips_and_routes(df)
    milages = [r.milage for r in routes]
    result_dicts = default_search(routes, limit)
    pairs_df = pairs_dataframe(result_dicts, milages)
    trips_df = trips_dataframe(trips, routes, milages)
    return (trips_df, pairs_df)


def default_pipeline(url, data_folder, days=None, types=None, limit=None):
    f = DataFolder(data_folder)
    f.download(url)
    trackpoints_csv = f.save_trackpoints()
    summaries_csv = f.save_summaries()
    df = make_subset(trackpoints_csv, summaries_csv, days, types)
    return default_results(df, limit)
