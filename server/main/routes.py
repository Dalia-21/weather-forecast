from flask import render_template, url_for, flash, redirect,\
    current_app, abort, request
import os
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
import re
from server.main.main import bp
from server.main.forms import LoginForm
from server.main.models import User
from server import login_manager
from scraper.scraping_tools import get_files, get_xml
from server import Session
from scraper.db_tools import get_table_type
import json
import plotly
import plotly.graph_objects as go


@bp.route('/')
@login_required
def index():
    current_app.logger.info("Collecting files for homepage.")
    files = get_files(names_only=True)
    current_app.logger.debug(f"File list: {files}")
    return render_template('index.html', files=files)


@bp.route('/file/<file_url>')
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


def get_line(entries, line_type):
    if line_type == "oldest":
        return [entry.oldest_data for entry in entries]
    elif line_type == "latest":
        return [entry.latest_data for entry in entries]
    elif line_type == "delta":
        return [entry.latest_data - entry.oldest_data for entry in entries]
    else:
        return []


def get_graph(request_data=None):
    data_titles = {'max_temp': "Maximum Temperature", 'min_temp': "Minimum Temperature",
                   'rainfall': "Rainfall", 'chance_of_rain': "Chance of Rain"}
    lines = []
    if not request_data:
        data_type = "max_temp"
        lines.append("delta")
    else:
        if request_data['data_type'] == 'None':
            data_type = "max_temp"
        else:
            data_type = request_data['data_type']
        if request_data['oldest']:
            lines.append("oldest")
        if request_data['latest']:
            lines.append("latest")
        if request_data['delta']:
            lines.append("delta")
    table = get_table_type(data_type)
    current_app.logger.debug(f"Data type: {data_type}")

    row_limit = Session.query(table).order_by(table.date).count() - 6
    entries = Session.query(table).order_by(table.date).limit(row_limit)
    dates = [entry.date for entry in entries]

    fig = go.Figure(
        data = [go.Scatter(x=dates, y=get_line(entries, line), name=line.capitalize()) for line in lines],
        layout = {"xaxis": {"title": "Date"}, "yaxis": {"title": "Forecast"}, "title": data_titles[data_type],
                  "height": 800}
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@bp.route('/graph', methods=['GET', 'POST'])
@login_required
def view_graph():
    return render_template('graphs/graph.html', graphJSON=get_graph())


@bp.route('/callback', methods=['POST'])
@login_required
def cb():
    current_app.logger.debug(f"JSON request: {request.json}")
    return get_graph(request.json)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        current_app.logger.debug(f"{form.user_name.data} attempting to login.")
        user = Session.query(User).filter_by(username=form.user_name.data).first()
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
    return Session.query(User).get(user_id)
