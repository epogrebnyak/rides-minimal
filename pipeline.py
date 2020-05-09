from rider import (
    FolderJSON,
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
    df_full = read_dataframe(full_csv)
    vehicle_type = wrap_vehicle_type(summaries_csv)
    subset_df = df_full
    if days:         
      subset_df = subset_by_dates(df_full, days)
    if types:
      subset_df = subset_by_vehicle_types(subset_df, types, vehicle_type)  
    return subset_df 

def pipeline(url, 
             days, 
             types, 
             json_folder,
             limit=None,
             filename_full_csv="df_full.csv",
             filename_summaries_csv="summaries.csv"):
    f = FolderJSON(json_folder)
    f.download(url)
    f.save_trackpoints(filename_full_csv)
    f.save_summaries(filename_summaries_csv)
    df = subset(filename_full_csv, filename_summaries_csv, days, types)
    return default_results(df, limit)
    
job=dict(url="https://github.com/epogrebnyak/rides-minimal/raw/master/sample_jsons/sample_jsons.rar",
             days=None, 
             types=None, 
             json_folder="data2/json", 
             limit=None,
             filename_full_csv="data2/df_full.csv",
             filename_summaries_csv="data2/summaries.csv")
         
(trips, routes, milages), (trips_df, pairs_df) = pipeline(**job)
print(trips_df)
print(pairs_df)