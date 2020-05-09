from rider import (
    FolderJSON,
    wrap_vehicle_type,
    get_dataframe,
    subset,
    get_trips_and_routes,
    trips_dataframe,
    result_dataframe,
    default_search,
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

try:
    what_is_vehicle_type 
except NameError:
    print("Читаем типы автомобилей")
    what_is_vehicle_type = wrap_vehicle_type("summaries.csv")

assert "freight" == what_is_vehicle_type("76727d5c-628d-4bcf-a24a-e5cf8a713426")


try:
    df_full
except NameError:
    print("Читаем данные о поездках (может быть долго)")
    df_full = get_dataframe("df_full.csv")

DAYS = ["2019-09-09"]
TYPES = ["freight"]
LIMIT = 10

print("Making subset")
subset_df = subset(df_full, DAYS, TYPES, what_is_vehicle_type)

print("Extracting routes // Преобразуем датафрейм в список поездок")
trips, routes = get_trips_and_routes(subset_df)

print("Calculating milage // Пробег по поездкам") 
milages = [r.milage for r in routes]

print("Saving trip start and end")
trips_dataframe(trips, routes, milages).to_csv("trips.csv")

print("Расчет попарных характеристик сближения поездок") 
result_dicts = default_search(routes, limit=LIMIT)

print("Формируем выгрузку результатов в CSV")
result_df = result_dataframe(result_dicts, milages)
result_df.to_csv("output.csv", index=None)

print("All doen // Все сделано.")
print("output.csv")
print("trips.csv")

