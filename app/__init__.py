from flask import Flask


def create_app(**kwargs):
    app = Flask(__name__)

    # config
    app.config['git_root'] = '/tmp/test/'

    # apply overrides passed to app factory
    for k, v in kwargs.iteritems():
        app.config[k] = v

    if app.config.get('ignore_auth', False):
        from .auth import KeyAuthContext
        app.no_auth_user = KeyAuthContext()
        app.no_auth_user.can_provision = True
        app.no_auth_user.can_create_repos = True
        app.no_auth_user.save()

    # routes
    from .routes import web as storage_container
    app.register_blueprint(storage_container, url_prefix='')

    return app