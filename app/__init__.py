from flask import Flask


def create_app():
    app = Flask(__name__)

    # config
    app.config['git_root'] = '/tmp/test/'

    # models

    # routes
    from .routes import web as storage_container
    app.register_blueprint(storage_container, url_prefix='')

    return app