import os

from git_subprocess import Repository
from . import utils

from flask import abort, Blueprint, current_app, jsonify, redirect, request, send_from_directory, url_for
from werkzeug import secure_filename

web = Blueprint('git_storage', __name__)

# Repository level

@web.route('/', methods=['GET', ])
def get_repos():
    """ Return a list of repositories
    """
    return jsonify({ 'repos': []})

@web.route('/', methods=['PUT', ])
def add_repo():
    """Create a new repository object

    Return {'url': '/<repo_id>/'}
    """
    name = utils.new_repo_name()

    repo = Repository(
        os.path.join(
            current_app.config.get('git_root'),
            name
        )
    )
    repo.init()

    return jsonify({
        'url': url_for('.get_repo', repo_id=name)
    })

@web.route('/<repo_id>/', methods=['DELETE', ])
def delete_repo(repo_id):
    """Delete the repository.

    This should remove access to the repository for all user, but allow recovery
    in the future.
    """

    return ''

@web.route('/<repo_id>/', methods=['GET', ])
def get_repo(repo_id):
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
    repo = Repository(
        os.path.join(
            current_app.config.get('git_root'),
            repo_id
        )
    )

    if not repo.is_valid_repo:
        abort(404)

    return jsonify({

    })

@web.route('/<repo_id>/', methods=['POST', ])
def update(repo_id):
    """ Given a dict a settings from ``get_repo_remote()``, update the settings.

    Partial dicts are allowed, and permissions must be verified first.
    """
    return ''

# File level

@web.route('/<repo_id>/<path:path>', methods=['GET', ])
def get_file(repo_id, path):
    """ Simple web request. Return the static file.
    """

    repo = get_repo(repo_id)

    path = path.split('/')
    if len(path) == 1:
        path = path[0]
        dirname = ''
    else:
        path = path[-1]
        dirname = '/'.join(path[:-1])


    return send_from_directory(
        directory=os.path.join(repo.path, dirname),
        filename=path,
    )

# @web.route('/<repo_id>/', methods=['PUT', ])
@web.route('/<repo_id>/<path:path>', methods=['PUT', ])
def add_file(repo_id, path=None):
    """ Adds a file to the repo at this path and commit."""
    # TODO: Consider implications of allowing a PUT to the repo level, with
    #       a dict containing the path.
    f = request.files.get('file')

    if not f or len(request.files) != 1:
        abort(400)

    repo = get_repo(repo_id)

    add_and_commit_file(repo, path, f)

    return jsonify({'url': url_for('.get_file', repo_id=repo_id, path=path)})

@web.route('/<repo_id>/<path:path>', methods=['POST', ])
def update_file(repo_id, path=None):
    return ''

@web.route('/<repo_id>/<path:path>', methods=['DELETE', ])
def delete_file(repo_id, path):
    repo = get_repo(repo_id)

    path_parts = path.split('/')
    fs_path = os.path.join(repo.path, *path_parts)

    if not os.path.isfile(fs_path):
        abort(404)

    repo.delete_file(
        file_path=os.path.join(*path_parts),
        commit_author='Test User <test@user.com>',
        commit_message='Test commit message',
    )

    return ''


def get_repo(id):
    return Repository(
        os.path.join(
            current_app.config.get('git_root'),
            id
        )
    )


def add_and_commit_file(repo, path, f):
    file_path, file_name = os.path.split(path)
    file_name = secure_filename(file_name)

    f.save(
        os.path.join(repo.path, file_path, file_name)
    )

    repo.add_file(
        file_path=os.path.join(file_path, file_name),
        commit_author='Test User <test@user.com>',
        commit_message='Test commit message',
    )