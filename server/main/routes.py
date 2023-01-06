from flask import render_template, url_for, flash, redirect,\
    current_app, abort
import os
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
import re

from server.main.main import bp
from server.main.forms import LoginForm
from server.main.models import User
from server import login_manager
from scraper.xml_tools import get_files, get_xml


@bp.route('/')
@login_required
def index():
    current_app.logger.info("Collecting files for homepage.")
    files = get_files(names_only=True)
    current_app.logger.debug(f"File list: {files}")
    return render_template('index.html', files=files)


@bp.route('/<file_url>')
@login_required
def view_file(file_url):
    # All file_urls follow the format 'dd-dd-dddd' (only 1 d for single digit dates)
    pattern = "\d{1,2}-\d{1,2}-\d{4}\Z"
    if not re.match(pattern, file_url):
        current_app.logger.warning(f"404 bad pattern: attempted to access {file_url}")
        abort(404)

    filename = current_app.config['DATA_SUBURB'] + '.' + file_url.replace('-', '.')
    current_app.logger.debug(f"Calling scraper.xml_tools.get_files with file {filename}")
    full_file_name = get_files(filename=filename)
    if not os.path.exists(full_file_name):
        current_app.logger.warning(f"404 file not found: attempted to access {file_url}")
        abort(404)

    data = get_xml(full_file_name)
    current_app.logger.debug(f"First data field: {data.area.find('forecast-period')}")
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
