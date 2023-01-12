from flask import Flask, render_template
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
import sys
from server_config import Config
from scraper.db_connection import get_session

Session = get_session(logging_mode=False)

migrate = Migrate()
login_manager = LoginManager()

def page_not_found(e):
    return render_template('404.html'), 404


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.register_error_handler(404, page_not_found)

    log_format = logging.Formatter(f'%(asctime)s %(levelname)s %(name)s : %(message)s')
    if app.config['DEBUG_MODE']:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
    else:
        handler = logging.StreamHandler(app.config['BASEDIR'] + "/logs/server_error.log")
        handler.setLevel(logging.ERROR)

    handler.setFormatter(log_format)
    logger = logging.getLogger()
    logger.addHandler(handler)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from server.main import main
    app.register_blueprint(main.bp)

    @app.teardown_appcontext
    def cleanup(resp_or_exec):
        Session.remove()

    return app
