from flask import render_template
import os
from server.main import bp
from bs4 import BeautifulSoup


@bp.route('/')
def index():
    # I want to shift this to config at some point, maybe make it an attribute of app
    files = os.listdir('/home/dalia/coding/weather-forecast/weather-data')
    return render_template('index.html', files=files)


@bp.route('/<file_url>')
def view_file(file_url):
    # Add check that file actually exists and implement 404
    # [except FileNotFoundError]
    filename = "Tullamarine." + file_url.split('-')[0] + '.' +\
               file_url.split('-')[1] + '.' + file_url.split('-')[2]
    full_file_path = "/home/dalia/coding/weather-forecast/weather-data/"
    with open(full_file_path + filename, 'r') as f:
        data = BeautifulSoup(f, "xml")
    return render_template('weather_file.html', filename=filename, data=data)