from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from scraper.scraping_tools import get_config
import logging


def get_engine(logging_mode=True):
    if not logging_mode:
        config_vars = get_config(option="server")
        return create_engine('sqlite:///' + config_vars['db'])
    else:
        config_vars = get_config(option="db")

    logger = config_vars['logger']
    if logger.level == logging.DEBUG:
        sql_echo = True
    else:
        sql_echo = False
    engine = create_engine('sqlite:///' + config_vars['db'], echo=sql_echo)
    return engine


def get_session(logging_mode=True):
    engine = get_engine(logging_mode=logging_mode)
    return scoped_session(sessionmaker(bind=engine))
