from flask import Blueprint

web = Blueprint('git_storage', __name__)

# Repository level

@web.route('/', methods=['PUT', ])
def add_repo():
    """Create a new repository object

    Return {'url': '/<repo_id>/'}
    """
    return ''

@web.route('/<repo_id>/', methods=['DELETE', ])
def delete_repo(repo_id):
    """Delete the repository.

    This should remove access to the repository for all user, but allow recovery
    in the future.
    """

    return ''

@web.route('/<repo_id>/', methods=['GET', ])
def get_repo_meta(repo_id):
    """Return information about the repo.

    Meta: (immutable through this endpoint)
        * file tree
        * date repo was created
        * list of users by access level
        * access level of current auth context

    Settings: (mutable)
        * list of users by access level
        * remote repos with which to sync
        * privacy setting: (public or private)
    """
    return ''

@web.route('/<repo_id>/', methods=['POST', ])
def update_repo_meta(repo_id):
    """ Given a dict a settings from ``get_repo_remote()``, update the settings.

    Partial dicts are allowed, and permissions must be verified first.
    """
    return ''

# File level

@web.route('/<repo_id>/<path:path>/', methods=['GET', ])
def get_file(repo_id, path):
    """ Simple web request. Return the static file.
    """
    auth = build_auth_context(data) # right now, only check for API key.
    return ''

# @web.route('/<repo_id>/', methods=['PUT', ])
@web.route('/<repo_id>/<path:path>/', methods=['PUT', ])
def add_file(repo_id, path=None):
    """ Adds a file to the repo at this path and commit."""
    # TODO: Consider implications of allowing a PUT to the repo level, with
    #       a dict containing the path.
    return ''

@web.route('/<repo_id>/<path:path>/', methods=['POST', ])
def update_file(repo_id, path=None):
    return ''

@web.route('/<repo_id>/<path:path>/', methods=['DELETE', ])
def delete_file(repo_id, path):
    return ''