from flask import render_template, url_for, flash, redirect,\
    current_app, abort
import os
from bs4 import BeautifulSoup
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash

from server.main.main import bp
from server.main.forms import LoginForm
from server.main.models import User
from server import login_manager
import re


@bp.route('/')
@login_required
def index():
    current_app.logger.info("Collecting files for homepage.")
    files = os.listdir(os.path.join(current_app.config['BASEDIR'], 'weather-data'))
    current_app.logger.debug(f"File list: {files}")
    return render_template('index.html', files=files)


@bp.route('/<file_url>')
@login_required
def view_file(file_url):
    # All file_urls follow the format 'dd-dd-dddd'
    pattern = "\d{2}-\d{2}-\d{4}\Z"
    if not re.match(pattern, file_url):
        current_app.logger.warning(f"404 bad pattern: attempted to access {file_url}")
        abort(404)
    filename = "Tullamarine." + file_url.split('-')[0] + '.' +\
               file_url.split('-')[1] + '.' + file_url.split('-')[2]
    full_file_path = current_app.config['BASEDIR'] + "/weather-data/"
    current_app.logger.debug(f"Path to weather files: {full_file_path}")
    full_file_name = os.path.join(full_file_path, filename)
    if not os.path.exists(full_file_name):
        current_app.logger.warning(f"404 file not found: attempted to access {file_url}")
        abort(404)
    with open(full_file_name, 'r') as f:
        data = BeautifulSoup(f, "xml")
    current_app.logger.debug(data)
    return render_template('weather_file.html', filename=filename, data=data)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        current_app.logger.debug(f"{form.user_name.data} attempting to login.")
        user = User.query.filter_by(username=form.user_name.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f"Welcome {user.username}")
        else:
            current_app.logger.warning(f"{form.user_name.data} attempted to access the site.")
            flash('Invalid username or password')
            return render_template('login.html', form=form)

        return redirect(url_for('main.index'))
    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
