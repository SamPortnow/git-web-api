from flask import Flask


def create_app():
    app = Flask(__name__)

    # config

    # models

    # routes
    from .routes import web as storage_container
    app.register_blueprint(storage_container, url_prefix='/tmp')

    return app