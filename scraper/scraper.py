import logging

from bs4 import BeautifulSoup
import urllib.request
import urllib.error
from contextlib import closing

from scraper.db_tools import add_entries_to_db
from scraper.scraping_tools import get_config
import argparse


def scrape(url, outfile, suburb, logger):
    """Scrape XML data from a certain URL,
    filter out the data for the weather station
    in the chosen suburb, and write it to the
    specified file."""

    logger.debug(f"Vars: {url}, {outfile}, {suburb}")
    try:
        with closing(urllib.request.urlopen(url)) as download:
            data = BeautifulSoup(download, "xml")
    except urllib.error.URLError:
        logger.error("Bad URL: request failed")
        return

    if not data:
        logger.error("XML data not obtained from site")
        return

    local_data = data.find("area", description=suburb)

    if not local_data:
        logger.error("Data for suburb not found or data format not as expected")
        return

    logger.debug(f"Data scraped: {local_data.find('forecast-period').attrs}")

    try:
        with open(outfile, "w") as f:
            f.write(str(local_data))
    except FileNotFoundError:
        logger.error("Directory not found: no data was recorded")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()
    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR
    s_vars = get_config(config_file="scrape-config.cfg", log_level=log_level)
    scrape(s_vars['url'], s_vars['outfile'], s_vars['suburb'], s_vars['logger'])
    add_entries_to_db(filename=s_vars['outfile'])
