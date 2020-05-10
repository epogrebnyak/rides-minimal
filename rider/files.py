"""Download and read JSON files."""

import csv
from pathlib import Path
import json
import os
from typing import Callable
import zipfile

from tqdm import tqdm
import requests

__all__ = ["dataprep"]


def make_filename(url):
    return url.split("/")[-1]


def get_from_web(url, file: str):
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


def unzip(file: str, folder: str):
    print("Unpacking JSON files to", folder)
    with zipfile.ZipFile(file, "r") as zip_ref:
        zip_ref.extractall(folder)
    print("Done")


def filenames(directory: str):
    return list(Path(directory).glob("*.json"))


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


def save_to_csv(filename, stream, keys):
    with open(filename, "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(tqdm(stream))


def save(getter: Callable, filename: str, source_folder: str):
    if not os.path.exists(filename):
        print("Creating", filename)
        keys = next(getter(source_folder)).keys()
        stream = getter(source_folder)
        save_to_csv(filename, stream, keys)
        print("Done")
    else:
        print("File already exists:", filename)
    return filename


def dataprep(url, directory):
    def path(filename):
        return os.path.join(directory, filename)

    json_dir = path("jsons")
    zipfile = path(make_filename(url))
    os.makedirs(json_dir, exist_ok=True)
    download(url, zipfile)
    if not filenames(json_dir):
        unzip(zipfile, json_dir)
    a = save(trackpoints, path("df_full.csv"), json_dir)
    b = save(summaries, path("summaries.csv"), json_dir)
    return a, b
