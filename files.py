def iterate(directory: str):
    for dict_ in yield_jsons(directory):
        for p in dict_["data"]:
            car = dict_["info"]["car_id"]
            ride = dict_["info"]["id"]
            yield dict(time=p[0], lat=p[2], lon=p[1], car=car, ride=ride)


def filenames(directory: str):
    return list(pathlib.Path(directory).glob("*.json"))


def yield_jsons(directory: str):
    for filename in filenames(directory):
        yield load_json(filename)


def load_json(filepath: str):
    """"Load a JSON file content"""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def summaries(folder: str):
    summary = lambda d: d["info"] 
    return pd.DataFrame(map(summary, yield_jsons(folder)))


def trackpoints(folder: str):
    return pd.DataFrame(iterate(folder))


def save(filename: str, getter: Callable, source_folder: str):
  if not os.path.exists(filename):
    print("Creating", filename)
    df = getter(source_folder)
    df.to_csv(filename, index=False)
    print("Saved", filename)
  print("File already exists:", filename)  