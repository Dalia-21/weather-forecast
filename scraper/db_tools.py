import logging
from scraper.scraping_tools import get_logger
logger = get_logger(log_level=logging.DEBUG)

from scraper.db_connection import get_session
from scraper.db_models import MaxTempEntry, MinTempEntry, RainfallEntry,\
    ChanceOfRainEntry, ProcessedFiles
from datetime import datetime
from scraper.scraping_tools import get_files, get_xml


session = get_session()


def add_entries_to_db(filename=None):
    if filename:
        file = get_files(filename=filename)
        logger.debug(f"Processing file {file}.")
        add_weather_entries(get_xml(file))
    else:
        files = get_files()
        for file in files:
            logger.debug(f"Processing file {file}")
            add_weather_entries(get_xml(file))

def add_weather_entries(data):
    global session
    file_date = data.area.find('forecast-period').attrs['start-time-local'][:10]
    if session.query(ProcessedFiles).filter_by(filedate=file_date).first():
        logger.debug(f"File for date {file_date} already processed.")
        return
    for period in data.area.find_all('forecast-period'):
        logger.debug(f"Processing data for file for date {file_date}")
        process_entries(period)

    logger.debug(f"Adding file for date {file_date} to processed files table.")
    f = ProcessedFiles(filedate=file_date)
    session.add(f)
    session.commit()


def get_table_type(data_type):
    if data_type == 'max_temp':
        data_table = MaxTempEntry
    elif data_type == 'min_temp':
        data_table = MinTempEntry
    elif data_type == 'rainfall':
        data_table = RainfallEntry
    elif data_type == 'chance_of_rain':
        data_table = ChanceOfRainEntry
    else:
        logger.error(f"Datatype {data_type} unknown.")
        return

    return data_table


def create_entry(date, index, entry, db_table):
    global session
    if index >= 4:
        db_entry = db_table(date=date, oldest_index=index, oldest_data=entry)
    else:
        db_entry = db_table(date=date, latest_index=index, latest_data=entry)

    logger.debug(f"Adding new entry for index {index}, date {date}, in table {db_table}")
    session.add(db_entry)
    session.commit()

def update_entry(existing_entry, index, new_entry):
    global session
    if index >= 4:
        existing_entry.oldest_index = index
        existing_entry.oldest_data = new_entry
    else:
        existing_entry.latest_index = index
        existing_entry.latest_data = new_entry

    logger.debug(f"Updating entry for index {index} for {existing_entry.date}.")
    session.commit()


def process_entry(date, index, entry, data_type=""):
    global session
    db_table = get_table_type(data_type)
    existing_entry = session.query(db_table).filter_by(date=date).first()
    if existing_entry:
        if index >= 4:
            if existing_entry.oldest_index and existing_entry.oldest_index > index:
                logger.debug(f"Row for date {date} already contains older index.")
            else:
                logger.debug(f"Updating {existing_entry.date} with data from index {index}")
                update_entry(existing_entry, index, entry)
                return
        else:
            if existing_entry.latest_index and existing_entry.latest_index < index:
                logger.debug(f"Row for date {date} already contains later index.")
            else:
                logger.debug(f"Updating {existing_entry.date} with data from index {index}")
                update_entry(existing_entry, index, entry)
                return
    else:
        create_entry(date, index, entry, db_table)

def process_entries(period):
    date = datetime.strptime(period.attrs['start-time-local'][:10], "%Y-%m-%d")
    index = int(period.attrs['index'])
    max_temp = period.find('element', type='air_temperature_maximum')
    min_temp = period.find('element', type='air_temperature_minimum')
    rainfall = period.find('element', type='precipitation_range')
    chance_of_rain = period.find('text', type='probability_of_precipitation')

    if max_temp:
        max_temp = int(max_temp.string)
        process_entry(date, index, max_temp, data_type="max_temp")
    else:
        logger.debug(f"No max_temp data for date {date} under index {index}.")
    if min_temp:
        min_temp = int(min_temp.string)
        process_entry(date, index, min_temp, data_type="min_temp")
    else:
        logger.debug(f"No min_temp data for date {date} under index {index}.")
    if rainfall:
        # d to d mm
        rainfall = float(rainfall.string.split()[2])
    else:
        rainfall = 0
    process_entry(date, index, rainfall, data_type="rainfall")
    if chance_of_rain:
        # dd%
        chance_of_rain = int(chance_of_rain.string[:-1])
    else:
        chance_of_rain = 0
    process_entry(date, index, chance_of_rain, data_type="chance_of_rain")

    logger.debug(f"Processed max_temp {max_temp}, min_temp {min_temp}, rainfall {rainfall} "
                 f"chance_of_rain {chance_of_rain} for index {index}, date {date}.")


def delete_table_entries(table):
    global session
    entries = session.query(table).all()
    for entry in entries:
        if entry.oldest_data is None or entry.latest_data is None:
            delta = datetime.today() - entry.date
            if delta.days >= 0:
                logger.debug(f"Deleting entry for date {entry.date} from table {table}")
                session.delete(entry)
                session.commit()


def cull_entries(table=None):
    if table:
        delete_table_entries(table)
    else:
        for table in [MaxTempEntry, MinTempEntry, RainfallEntry, ChanceOfRainEntry]:
            delete_table_entries(table)


if __name__ == '__main__':
    logger.debug("Calling main db loop function.")
    add_entries_to_db()
    cull_entries()
    session.close()
