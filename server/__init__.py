from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from server_config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def page_not_found(e):
    return render_template('404.html'), 404


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.register_error_handler(404, page_not_found)

    log_format = f'%(asctime)s %(levelname)s %(name)s : %(message)s'
    if app.config['DEBUG_MODE']:
        log_level = logging.DEBUG
        log_file = None
    elif not app.config['DEBUG_MODE']:
        log_level = logging.ERROR
        log_file = app.config['BASEDIR'] + "/logs/server_error.log"

    print(app.config['DEBUG_MODE'], log_level, log_file)
    logging.basicConfig(filename=log_file, level=log_level, format=log_format)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from server.main import main
    app.register_blueprint(main.bp)

    return app
