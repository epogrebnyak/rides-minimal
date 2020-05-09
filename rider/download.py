from pathlib import Path
import requests
import os
import zipfile

__all__ = ["download_and_unzip"]


def make_filename(url):
    return Path(url.split("/")[-1])


def get_from_web(url, file: Path):
    print("Downloading", url)
    r = requests.get(url)
    file.write_bytes(r.content)
    print("Downloaded", file, "from", url)


def download(url: str) -> str:
    file = make_filename(url)
    if file.exists():
        print("File already exists:", file)
    else:
        get_from_web(url, file)
    return str(file)


def unzip(file, folder):
    print("Unpacking JSON files")
    with zipfile.ZipFile(file, "r") as zip_ref:
        zip_ref.extractall(folder)
    print("Done unpacking JSON files to folder:", folder)


def download_and_unzip(url: str, destination_folder: str):
    path = download(url)
    os.makedirs(destination_folder, exist_ok=True)
    unzip(path, destination_folder)
    return destination_folder
