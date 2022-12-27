from flask import render_template
import os
from server import app # might need to change this name


@app.route('/')
def index():
    # I want to shift this to config at some point, maybe make it an attribute of app
    files = os.listdir('/home/dalia/coding/weather-forecast/weather-data')
    return render_template('index.html', files=files)


@app.route('/<file_url>')
def view_file(file_url):
    # Add check that file actually exists and implement 404
    return '<h1>' + file_url + '</h1>'