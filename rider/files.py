"""Read JSON files."""

from pathlib import Path
import json
import os
from typing import Callable
from dataclasses import dataclass

from tqdm import tqdm

__all__ = ["FolderJSON"]


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
    import csv

    with open(filename, "w", encoding="utf-8") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(tqdm(stream))


def save(filename: str, getter: Callable, source_folder: str):
    if not os.path.exists(filename):
        print("Creating", filename)
        keys = next(getter(source_folder)).keys()
        stream = getter(source_folder)
        save_to_csv(filename, stream, keys)
        print("Saved", filename)
    print("File already exists:", filename)


@dataclass
class FolderJSON:
    directory: str

    def download(self, url: str):
        from .download import download_and_unzip

        download_and_unzip(url, self.directory)

    def save_trackpoints(self, path: str):
        save(path, trackpoints, self.directory)

    def save_summaries(self, path: str):
        save(path, summaries, self.directory)
