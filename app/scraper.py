from bs4 import BeautifulSoup
import urllib.request
import urllib.error
from contextlib import closing
from datetime import date
import logging


def scrape(url, outfile, suburb, logger):
    """Scrape XML data from a certain URL,
    filter out the data for the weather station
    in the chosen suburb, and write it to the
    specified file."""

    data = ""
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

    if not local_data:
        logger.error("Data for suburb not found or data format not as expected")
        return

    try:
        with open(outfile, "w") as f:
            f.write(local_data)
    except FileNotFoundError:
        logger.error("File not found: no data was recorded")



if __name__ == '__main__':
    # need to check if this filename changes and potentially scrape new url each day
    bom_url = "ftp://ftp.bom.gov.au/anon/gen/fwo/IDV10753.xml"
    today = date.today()
    # All this needs to move to a config file
    suburb = "Tullamarine"
    logging_file = "/home/ubuntu/weather-forecast/logs/weather.log"
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename=logging_file, format=log_format, level=logging.ERROR)
    error_logger = logging.getLogger()
    # this needs to change to a command line argument soon
    outfile = f"/home/ubuntu/weather-forecast/weather-data/{suburb}.{today.day}.{today.month}.{today.year}"
    scrape(bom_url, outfile, suburb, error_logger)
