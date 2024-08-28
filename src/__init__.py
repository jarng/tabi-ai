import os

from flask import Flask
from werkzeug.exceptions import BadRequest

from .config import config
from .api import api as api_blueprint
from .errors import *
from .core.llm import LangChain


def create_app(config_name) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    LangChain.init_app(app)
    llm = LangChain.get_instance()
    llm.init_vector_db()

    # health
    @app.route("/health")
    def health():
        return "ok"

    # api
    app.register_blueprint(api_blueprint, url_prefix="/api/v1")

    # error handlers
    app.register_error_handler(BadRequest.code, handle_bad_request)

    return app
