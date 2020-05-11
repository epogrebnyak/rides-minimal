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

RAW_DATA_URL = (
    "https://dl.dropboxusercontent.com"
    "/sh/hibzl6fkzukltk9/AABTFmhvDvxyQdUaBsKl4h59a"
    "/data_samples_json.zip"
)

print("Started reading data")

f = FolderJSON("data")
f.download(RAW_DATA_URL)
f.save_trackpoints("df_full.csv")
f.save_summaries("summaries.csv")


DAYS = ["2019-09-09"]
TYPES = ["freight"]
LIMIT = 10


try:
    df_full
except NameError:
    print("Читаем данные о поездках (может быть долго)")
    df_full = read_dataframe("df_full.csv")

print("Читаем типы автомобилей")
vehicle_type = wrap_vehicle_type("summaries.csv")
assert "freight" == vehicle_type("76727d5c-628d-4bcf-a24a-e5cf8a713426")

print("Making subset")
subset_df = subset_by_dates(df_full, DAYS)
subset_df = subset_by_vehicle_types(subset_df, TYPES, vehicle_type)

print("Extracting routes // Преобразуем датафрейм в список поездок")
trips, routes = get_trips_and_routes(subset_df)

print("Calculating milage // Пробег по поездкам")
milages = [r.milage for r in routes]

print("Расчет попарных характеристик сближения поездок")
result_dicts = default_search(routes, limit=LIMIT)

print("Формируем выгрузку результатов в CSV")
pairs_df = pairs_dataframe(result_dicts, milages)
trips_df = trips_dataframe(trips, routes, milages)

print("Saving CSV files")
pairs_df.to_csv("output.csv", index=None)
trips_df.to_csv("trips.csv")

print("All done // Все сделано.")
print("output.csv")
print("trips.csv")
