from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from scraping_tools import get_config
import logging


def get_engine():
    config_vars = get_config(option="db")
    logger = config_vars['logger']
    if logger.level == logging.DEBUG:
        sql_echo = True
    else:
        sql_echo = False
    engine = create_engine('sqlite:///' + config_vars['db'], echo=sql_echo)
    return engine


def get_session():
    engine = get_engine()
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    return session
