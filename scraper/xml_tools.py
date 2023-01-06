from bs4 import BeautifulSoup
import os


def get_files(relative_path='../weather-data', filename=None, names_only=False):
    current_path = os.path.dirname(__file__)
    path_to_files = os.path.join(current_path, relative_path)
    if filename:
        return os.path.join(path_to_files, filename)
    elif names_only:
        return os.listdir(path_to_files)
    else:
        return sorted([os.path.join(path_to_files, file) for file in os.listdir(path_to_files)])


def get_xml(file):
    with open(file, "r") as f:
        return BeautifulSoup(f, "xml")
