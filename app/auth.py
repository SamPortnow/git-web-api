from hashlib import sha1 as sha
from random import SystemRandom

from flask import current_app, request
from modularodm import StoredObject, fields


from .db import db

# Use permanent API keys to associate abstract users with credentials.

# Where are author and email stored?

# This side - how can we subscribe to changes on the source system?

# Client site - what are the implications of trusting them?


class AuthContext(object):

    @property
    def ssh_private_key(self):
        raise NotImplementedError

    @property
    def ssh_public_key(self):
        raise NotImplementedError

    @property
    def full_name(self):
        raise NotImplementedError

    @property
    def email(self):
        raise NotImplementedError

    def can_read_repo(self, repo_id):
        raise NotImplementedError

    def can_modify_repo(self, repo_id):
        raise NotImplementedError

    def is_repo_admin(self, repo_id):
        raise NotImplementedError

    @property
    def can_create_repos(self):
        raise NotImplementedError


class PublicAuthContext(AuthContext):
    _id = None

    def can_read_repo(self, repo_id):
        return RepoMeta.load(repo_id).is_public

    def can_modify_repo(self, repo_id):
        return False

    def is_repo_admin(self, repo_id):
        return False

    can_create_repos = False


class KeyAuthContext(StoredObject, AuthContext):
    _id = fields.StringField(primary=True)
    can_provision = fields.BooleanField(default=False)
    can_create_repos = fields.BooleanField(default=False)

    def can_read_repo(self, repo_id):

        for field in ['admin_repos', 'read_repos', 'write_repos']:
            try:
                for ref in getattr(self, field).get('repometa', []):
                    if repo_id in getattr(self, field)['repometa'][ref]:
                        return True
            except AttributeError:
                pass

        return RepoMeta.load(repo_id).is_public

    def __init__(self, *args, **kwargs):
        super(KeyAuthContext, self).__init__(*args, **kwargs)
        self._id = sha( str(SystemRandom().random()) ).hexdigest()

KeyAuthContext.set_storage(db)


class RepoMeta(StoredObject):
    _meta = {
        'optimistic': True
    }

    _id = fields.StringField(primary=True)
    is_public = fields.BooleanField(default=False)
    access_read = fields.ForeignField(
        'KeyAuthContext',
        backref='read_repos',
        list=True,
    )
    access_write = fields.ForeignField(
        'KeyAuthContext',
        backref='write_repos',
        list=True,
    )
    access_admin = fields.ForeignField(
        'KeyAuthContext',
        backref='admin_repos',
        list=True,
    )

RepoMeta.set_storage(db)


def get_auth_context():
    """ Return an instance of a descendant of AuthContext.
    """
    # TODO: Make this work :)
    if current_app.config.get('ignore_auth', False):
        return current_app.no_auth_user

    try:
        context = KeyAuthContext.load(request.args.get('key'))
        return context
    except KeyError:
        return PublicAuthContext()