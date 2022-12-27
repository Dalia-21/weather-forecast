from flask import render_template
import os
from server.main import bp


@bp.route('/')
def index():
    # I want to shift this to config at some point, maybe make it an attribute of app
    files = os.listdir('/home/dalia/coding/weather-forecast/weather-data')
    return render_template('index.html', files=files)


@bp.route('/<file_url>')
def view_file(file_url):
    # Add check that file actually exists and implement 404
    return '<h1>' + file_url + '</h1>'