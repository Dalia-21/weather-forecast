from flask import render_template, url_for, abort, flash, \
    request, redirect, current_app
import os
from server.main.main import bp
from bs4 import BeautifulSoup
from server.main.forms import LoginForm
from werkzeug.security import check_password_hash
from server.main.models import User
from flask_login import login_user, logout_user


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


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.user_name.data).first()
        if check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f"Welcome {user.username}")
        else:
            flash('Invalid username or password')
            return render_template('login.html', form=form)

        return redirect(url_for('main.index'))
    return render_template('login.html', form=form)