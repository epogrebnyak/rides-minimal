from rider import (
    DataFolder,
    wrap_vehicle_type,
    read_dataframe,
    subset_by_dates,
    subset_by_vehicle_types,
    get_trips_and_routes,
    default_search,
    trips_dataframe,
    pairs_dataframe,
)


def default_results(df, limit=None):
    trips, routes = get_trips_and_routes(df)
    milages = [r.milage for r in routes]
    result_dicts = default_search(routes, limit)
    pairs_df = pairs_dataframe(result_dicts, milages)
    trips_df = trips_dataframe(trips, routes, milages)
    return (trips, routes, milages), (trips_df, pairs_df)


def subset(full_csv, summaries_csv, days, types):
    subset_df = read_dataframe(full_csv)
    if days:
        subset_df = subset_by_dates(subset_df, days)
    if types:
        vehicle_type = wrap_vehicle_type(summaries_csv)
        subset_df = subset_by_vehicle_types(subset_df, types, vehicle_type)
    return subset_df


def pipeline(
    url,    
    data_folder,
    days=None,
    types=None,
    limit=None
):
    f = DataFolder(data_folder)
    f.download(url)
    a = f.save_trackpoints()
    b = f.save_summaries()
    df = subset(a, b, days, types)
    return default_results(df, limit)
