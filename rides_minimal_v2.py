from rider import (
    FolderJSON,
    wrap_vehicle_type,
    get_dataframe,
    subset,
    get_trips_and_routes,
    milage,
    trips_dataframe,
    result_dataframe,
    default_search,
)


RAW_DATA_URL = (
    "https://dl.dropboxusercontent.com"
    "/sh/hibzl6fkzukltk9/AABTFmhvDvxyQdUaBsKl4h59a"
    "/data_samples_json.zip"
)

f = FolderJSON("data")
f.download(RAW_DATA_URL)
f.save_trackpoints("df_full.csv")
f.save_summaries("summaries.csv")

try:
    vehicle_type
except NameError:
    print("Читаем типы автомобилей")
    vehicle_type = wrap_vehicle_type("summaries.csv")

assert "freight" == vehicle_type("76727d5c-628d-4bcf-a24a-e5cf8a713426")


try:
    df_full
except NameError:
    print("Читаем данные о поездках")
    df_full = get_dataframe("df_full.csv")

print("Making subset")
days = ["2019-09-09"]
types = ["freight"]
subset_df = subset(df_full, days, types, vehicle_type)

print("Extracting routes")
# Преобразуем датафрейм в список поедок
trips, routes = get_trips_and_routes(subset_df)

print("Calculating milage")
# Пробег по поездкам
milages = [milage(r) for r in routes]

print("Saving trip start and end")
trips_dataframe(trips, routes, milages).to_csv("trips.csv")

print("Расчет попарных характеристик поездок") 
result_dicts = default_search(routes, limit=None)

print("Формируем выгрузку данных в csv")
result_df = result_dataframe(result_dicts, milages)
result_df.to_csv("output.csv", index=None)
