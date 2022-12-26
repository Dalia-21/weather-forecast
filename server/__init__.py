from flask import Flask
from flask import render_template
import os


app = Flask(__name__)


@app.route('/')
def index():
    # I want to shift this to config at some point, maybe make it an attribute of app
    files = os.listdir('/home/ubuntu/weather-forecast/weather-data')
    return render_template('index.html', files=files)