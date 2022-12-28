import os
from dotenv import dotenv_values


basedir = os.path.abspath(os.path.dirname(__file__))
env = dotenv_values(basedir + '.env')


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'INSERT_SECRET_KEY_HERE'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'server.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASEDIR = basedir
    if env:
        DEBUG_MODE = env['FLASK_DEBUG']
    else:
        DEBUG_MODE = False