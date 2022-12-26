from flask import render_template
import os
from server import app # might need to change this name


@app.route('/')
def index():
    # I want to shift this to config at some point, maybe make it an attribute of app
    files = os.listdir('/home/ubuntu/weather-forecast/weather-data')
    return render_template('index.html', files=files)