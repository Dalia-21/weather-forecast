import configparser
import logging
from bs4 import BeautifulSoup
import os
from datetime import date


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


def get_logger(log_level=logging.ERROR, logfile="/home/dalia/coding/weather-forecast/logs/weather.log"):
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if log_level == logging.DEBUG:
        log_file = None
    else:
        log_file = logfile
    logging.basicConfig(filename=log_file, format=log_format, level=log_level)
    return logging.getLogger()


def get_config(config_file="scrape-config.cfg", log_level=logging.ERROR, option="all"):
    basedir = os.path.abspath(os.path.dirname(__file__))
    parser = configparser.ConfigParser()
    parser.read(basedir + "/" + config_file)

    config_vars = dict()
    config_vars['logger'] = get_logger(log_level=log_level, logfile=parser['Settings']['LogFile'])
    if option=="logging":
        return config_vars

    config_vars['db'] = parser['DB']['DB_URI']
    if option == "db":
        return config_vars

    today = date.today()
    output_dir = parser['FTP']['OutputDir']
    suburb = parser['FTP']['Suburb']
    outfile = f"{output_dir}{suburb}.{today.day}.{today.month}.{today.year}"
    config_vars['url'] = parser['FTP']['Url']
    config_vars['suburb'] = suburb
    config_vars['outfile'] = outfile

    return config_vars
