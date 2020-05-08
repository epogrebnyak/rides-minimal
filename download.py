import pathlib
import os
import zipfile

def make_filename(url):
  return pathlib.Path(url.split("/")[-1])

def get_from_web(url, file:pathlib.Path):
    r = requests.get(url)
    file.write_bytes(r.content)
    print("Downloaded", file, "from", url)

def download(url):
  file = make_filename(url)
  if file.exists():
    print("File already exists:", file)   
  else: 
    get_from_web(url, file)
  return str(file)

def unzip(file, folder):        
    print("Unpacking JSON files")
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(folder)
    print("Done unpacking JSON files to folder:", folder)


def download_and_unzip(url: str, destination_folder: str):
  path = download(url)
  if not os.path.exists(destination_folder):
    os.mkdir(destination_folder)
    unzip (path, destination_folder)
  else:
    print ("Folder already exists:", destination_folder)   
  return destination_folder