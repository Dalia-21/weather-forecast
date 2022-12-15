from bs4 import BeautifulSoup
import urllib.request
import urllib.error
from contextlib import closing
from datetime import date
import logging
import configparser
import argparse


def scrape(url, outfile, suburb, logger):
    """Scrape XML data from a certain URL,
    filter out the data for the weather station
    in the chosen suburb, and write it to the
    specified file."""

    try:
        with closing(urllib.request.urlopen(url)) as download:
            data = BeautifulSoup(download, "xml")
    except urllib.error.URLError:
        logger.error("Bad URL: request failed")
        return

    if not data:
        logger.error("XML data not obtained from site")
        return

    local_data = str(data.find("area", description=suburb))

    if local_data == 'None':
        logger.error("Data for suburb not found or data format not as expected")
        return

    try:
        with open(outfile, "w") as f:
            f.write(local_data)
    except FileNotFoundError:
        logger.error("File not found: no data was recorded")


def get_config(config_file, logfile=None, log_level=logging.ERROR):
    """Takes path to a config file and optionally a logging level
    and returns a dictionary of values to pass to the scrape function."""

    parser = configparser.ConfigParser()
    parser.read(config_file)
    output_dir = parser['FTP']['OutputDir']
    suburb = parser['FTP']['Suburb']
    today = date.today()
    outfile = f"{output_dir}{suburb}.{today.day}.{today.month}.{today.year}"
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file = logfile or parser['Settings']['LogFile']
    logging.basicConfig(filename=log_file, format=log_format, level=log_level)
    logger = logging.getLogger()
    scrape_vars = dict()
    scrape_vars['url'] = parser['FTP']['Url']
    scrape_vars['suburb'] = suburb
    scrape_vars['outfile'] = outfile
    scrape_vars['logger'] = logger
    return scrape_vars


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("config_filename")
    arg_parser.add_argument("-l", "--logfile")
    args = arg_parser.parse_args()
    config_filename = args.config_filename or '/home/ubuntu/weather-forecast/app/ftp-config.cfg'
    s_vars = get_config(config_filename, args.logfile)
    scrape(s_vars['url'], s_vars['outfile'], s_vars['suburb'], s_vars['logger'])
