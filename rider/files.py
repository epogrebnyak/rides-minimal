"""Download and read JSON files."""

import csv
from pathlib import Path
import json
import os
from typing import Callable, List, Tuple
import zipfile

from tqdm import tqdm  # type: ignore
import requests  # type: ignore

__all__ = ["dataprep"]


def warn_if_exists(*args, **kwargs):
    raise NotImplementedError("Decorator for if not os.path.exists case.")


def make_filename(url: str) -> str:
    return url.split("/")[-1]


def get_from_web(url, file: str) -> None:
    print("Downloading", url)
    r = requests.get(url)
    print("Writing to", file)
    Path(file).write_bytes(r.content)
    print("Done")


def download(url: str, file: str) -> str:
    if os.path.exists(file):
        print("File already exists:", file)
    else:
        get_from_web(url, file)
    return file


def unzip(file: str, folder: str) -> None:
    print("Unpacking JSON files to", folder)
    with zipfile.ZipFile(file, "r") as zip_ref:
        zip_ref.extractall(folder)
    print("Done")


def filenames(directory: str) -> List[str]:
    return [str(x) for x in Path(directory).glob("*.json")]


def load_json(filepath: str):
    """"Load JSON file contents."""
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def yield_jsons(directory: str):
    for filename in filenames(directory):
        yield load_json(filename)


def trackpoints(directory: str):
    for dict_ in yield_jsons(directory):
        for p in dict_["data"]:
            yield dict(
                time=p[0],
                lat=p[2],
                lon=p[1],
                car=dict_["info"]["car_id"],
                ride=dict_["info"]["id"],
            )


def summaries(folder: str):
    summary = lambda d: d["info"]
    return map(summary, yield_jsons(folder))


def save_to_csv(filename: str, stream, keys: List[str]):
    with open(filename, "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(tqdm(stream))


def _save(getter: Callable, source_folder: str, filename: str):
    print("Creating", filename)
    keys = next(getter(source_folder)).keys()
    stream = getter(source_folder)
    save_to_csv(filename, stream, keys)
    print("Done")


def save(getter: Callable, source_folder: str, filename: str) -> str:
    if os.path.exists(filename):
        print("File already exists:", filename)
    else:
        _save(getter, source_folder, filename)
    return filename


def dataprep(
    url: str,
    directory: str,
    json_dirname: str = "jsons",
    trackpoints_csv: str = "df_full.csv",
    summaries_csv: str = "summaries.csv",
) -> Tuple[str, str]:
    """
    Prepare data using *url*. 
    Save data files at *directory*, re-use files if they exist.
    Return paths to two CSV files.
    """

    def path(filename):
        return os.path.join(directory, filename)

    json_dir = path(json_dirname)
    zipfile = path(make_filename(url))
    os.makedirs(json_dir, exist_ok=True)
    download(url, zipfile)
    if not filenames(json_dir):
        unzip(zipfile, json_dir)
    a = save(trackpoints, json_dir, path(trackpoints_csv))
    b = save(summaries, json_dir, path(summaries_csv))
    return a, b
