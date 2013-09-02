import httplib as http
import os
from StringIO import StringIO
from urlparse import urlparse, parse_qs


from flask import abort, Blueprint, current_app, jsonify, redirect, request, send_file, send_from_directory, url_for, make_response
from git_subprocess import Repository
from werkzeug.utils import secure_filename

from auth import get_auth_context, RepoMeta

web = Blueprint('git_storage', __name__)

# Repository level

@web.route('/', methods=['GET', ])
def get_repos():
    """ Return a list of repositories
    """
    auth_context = get_auth_context()

    repos = [
        x for x in os.listdir(current_app.config.get('git_root'))
        if (
            os.path.isdir(os.path.join(current_app.config.get('git_root'), x))
            and auth_context.can_read_repo(x)
        )
    ]

    return jsonify({'repos': repos})

@web.route('/', methods=['PUT', ])
def add_repo():
    """Create a new repository object

    Return {'url': '/<repo_id>/'}
    """

    auth_context = get_auth_context()

    if not auth_context.can_create_repos:
        return abort(http.UNAUTHORIZED)

    meta = RepoMeta()
    meta.is_public = bool(request.form.get('is_public'))
    meta.access_admin.append(auth_context)

    meta.save()

    name = meta._id

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

    return abort(500)

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
    auth_context = get_auth_context()

    try:
        if not auth_context.can_read_repo(repo_id):
            return abort(http.UNAUTHORIZED)
    except KeyError:
        pass

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
def update_repo(repo_id):
    """ Given a dict a settings from ``get_repo_remote()``, update the settings.

    Partial dicts are allowed, and permissions must be verified first.
    """
    return ''

# File level

@web.route('/<repo_id>/<path:path>', methods=['GET', ])
def get_file(repo_id, path):
    """ Simple web request. Return the static file.
    """
    auth_context = get_auth_context()

    if not auth_context.can_read_repo(repo_id):
        return abort(http.UNAUTHORIZED)

    repo = get_repo(repo_id)

    if request.args.get('info') is not None:
        return jsonify({
            'versions': [v.sha for v in repo.get_file(path).versions]
        })

    if request.args.get('sha'):
        sha = request.args.get('sha')
        f = repo.get_file(path)
        if sha not in [x.sha for x in f.versions]:
            abort(http.NOT_FOUND)
        else:
            return send_file(StringIO(f.get_version_by_sha(sha).content))

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
    auth_context = get_auth_context()

    if not auth_context.can_write_repo(repo_id):
        return abort(http.UNAUTHORIZED)

    f = request.files.get('file')

    if not f or len(request.files) != 1:
        abort(400)

    repo = get_repo(repo_id)
    path = urlparse(path).path

    add_and_commit_file(repo, path, f,
                        author_name=auth_context.full_name,
                        author_email=auth_context.email,
    )

    return jsonify({'url': url_for('.get_file', repo_id=repo_id, path=path)})

@web.route('/<repo_id>/<path:path>', methods=['DELETE', ])
def delete_file(repo_id, path):
    auth_context = get_auth_context()

    if not auth_context.can_write_repo(repo_id):
        return abort(http.UNAUTHORIZED)

    repo = get_repo(repo_id)

    path_parts = path.split('/')
    fs_path = os.path.join(repo.path, *path_parts)

    if not os.path.isfile(fs_path):
        abort(404)

    repo.delete_file(
        file_path=os.path.join(*path_parts),
        commit_author='{} <{}>'.format(
            auth_context.full_name,
            auth_context.email
        ),
        commit_message='Deleted {}'.format(os.path.join(*path_parts)),
    )

    resp = make_response()
    resp.status_code = http.NO_CONTENT
    return resp


def get_repo(id):
    return Repository(
        os.path.join(
            current_app.config.get('git_root'),
            id
        )
    )


def add_and_commit_file(repo, path, f, author_name=None, author_email=None):
    file_path, file_name = os.path.split(path)
    file_name = secure_filename(file_name)

    if author_name and author_email:
        commit_message = '{} <{}>'.format(author_name, author_email)
    else:
        commit_message = 'Unknown User <unknown@domain.com>'

    f.save(
        os.path.join(repo.path, file_path, file_name)
    )

    repo.add_file(
        file_path=os.path.join(file_path, file_name),
        commit_author=commit_message,
        commit_message='Test commit message',
    )