from bs4 import BeautifulSoup
import urllib.request
from contextlib import closing
from datetime import date


def scrape(url, outfile, suburb):
    """Scrape XML data from a certain URL,
    filter out the data for the weather station
    in the chosen suburb, and write it to the
    specified file."""

    # these operations should all be try, except loops
    with closing(urllib.request.urlopen(url)) as download:
        data = BeautifulSoup(download, "xml")

    local_data = str(data.find("area", description=suburb))

    if not local_data:
        # implement error logging and notification
        return

    with open(outfile, "w") as f:
        f.write(local_data)



if __name__ == '__main__':
    # need to check if this filename changes and potentially scrape new url each day
    bom_url = "ftp://ftp.bom.gov.au/anon/gen/fwo/IDV10753.xml"
    today = date.today()
    suburb = "Tullamarine"
    # this needs to change to a command line argument soon
    outfile = f"/home/ubuntu/weather-forecast/weather-data/{suburb}.{today.day}.{today.month}.{today.year}"
    scrape(bom_url, outfile, suburb)
