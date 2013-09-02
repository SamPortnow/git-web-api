import httplib as http
from StringIO import StringIO

from flask import json

from tests import GWATestCase
from app import create_app
from app.auth import KeyAuthContext


class AuthTestCase(GWATestCase):
    def _fake_file(self, content=None, filename=None):
        return StringIO(content or 'my file contents'), 'test.txt'

    def setUp(self):
        super(AuthTestCase, self).setUp()
        self.app = create_app().test_client()

        self.read_user = KeyAuthContext()
        self.read_user.can_create_repos = False
        self.read_user.save()

        self.second_user = KeyAuthContext()
        self.second_user.can_create_repos = True
        self.second_user.save()

    # Repo Creation
    ###############

    def test_create_repo_fail_anonymous(self):
        resp = self.app.put('/')

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_create_repo_fail_unauthorized(self):
        resp = self.app.put('/?key=' + self.read_user._id)

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_create_repo_authorized(self):
        resp = self.app.put('/?key=' + self.user._id)

        self.assertEqual(
            resp.status_code,
            http.OK
        )

    def test_create_repo_write_key(self):
        write_key = json.loads(
            self.app.put('/?key=' + self.user._id).data
        )['write_key']

        self.assertIsNotNone(
            write_key
        )

    # Repo Listing
    ##############

    def test_list_private_repo_anonymous(self):
        json.loads(
            self.app.put('/?key=' + self.user._id).data
        ).get('url')

        self.assertEqual(
            json.loads(self.app.get('/').data).get('repos'),
            []
        )

    def test_list_private_repo_authorized(self):
        json.loads(
            self.app.put('/?key=' + self.user._id).data
        ).get('url')

        repos = json.loads(
            self.app.get('/?key=' + self.user._id).data
        ).get('repos')

        self.assertEqual(len(repos), 1)

    def test_list_private_repo_unauthorized(self):
        json.loads(
            self.app.put('/?key=' + self.user._id).data
        ).get('url')

        repos = json.loads(
            self.app.get('/?key=' + self.second_user._id).data
        ).get('repos')

        self.assertEqual(len(repos), 0)

    def test_list_public_repo(self):

        self.app.put(
            '/?key=' + self.user._id,
            data={'is_public': 1}
        )

        repos = json.loads(
            self.app.get('/').data
        ).get('repos')

        self.assertEqual(len(repos), 1)

    # Repo Read
    ###########

    def test_read_repo_private_authorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        resp = self.app.get(
            repo_url + '?key={}'.format(self.user._id)
        )

        self.assertEqual(
            resp.status_code,
            http.OK
        )

    def test_read_repo_private_unauthorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        resp = self.app.get(repo_url + '?key={}'.format(self.second_user._id))

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_read_repo_private_anonymous(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        resp = self.app.get(repo_url)

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    # File Creation
    ###############

    def test_create_file_private_authorized(self):
        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        resp = self.app.put(
            repo_url + 'foo.txt?key={}'.format(self.user._id),
            data={
                'file': self._fake_file(),
                'full_name': 'Test User',
                'email': 'test_user@domain.com',
            }
        )

        self.assertEqual(
            resp.status_code,
            http.OK
        )

    def test_create_file_private_unauthorized(self):
        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        resp = self.app.put(
            repo_url + 'foo.txt?key={}'.format(self.second_user._id),
            data={'file': self._fake_file()}
        )

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_create_file_private_anonymous(self):
        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        resp = self.app.put(
            repo_url + 'foo.txt',
            data={'file': self._fake_file()}
        )

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    # File Read
    ###########

    def test_read_file_private_authorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        resp = self.app.get(file_url + '?key={}'.format(self.user._id))

        self.assertEqual(
            resp.status_code,
            http.OK
        )

    def test_read_file_private_unauthorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        resp = self.app.get(file_url + '?key={}'.format(self.second_user._id))

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_read_file_private_anonymous(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        resp = self.app.get(file_url)

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_read_file_info_private_authorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        resp = self.app.get(file_url + '?info=1&key={}'.format(self.user._id))

        self.assertEqual(
            resp.status_code,
            http.OK
        )

    def test_read_file_info_private_unauthorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        resp = self.app.get(file_url + '?info=1&key={}'.format(self.second_user._id))

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_read_file_info_private_anonymous(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        resp = self.app.get(file_url + '?info=1')

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_read_file_version_private_authorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        sha = json.loads(
            self.app.get(file_url + '?info=1&key={}'.format(self.user._id)).data
        )['versions'][0]

        resp = self.app.get(
            file_url + '?version={}1&key={}'.format(sha, self.user._id)
        )

        self.assertEqual(
            resp.status_code,
            http.OK
        )

    def test_read_file_version_private_unauthorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        sha = json.loads(
            self.app.get(file_url + '?info=1&key={}'.format(self.user._id)).data
        )['versions'][0]

        resp = self.app.get(
            file_url + '?version={}1&key={}'.format(sha, self.second_user._id)
        )

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_read_file_version_private_anonymous(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        sha = json.loads(
            self.app.get(file_url + '?info=1&key={}'.format(self.user._id)).data
        )['versions'][0]

        resp = self.app.get(
            file_url + '?version={}1'.format(sha)
        )

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    # File Deletion
    ###############

    def test_delete_file_private_authorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        resp = self.app.delete(
            file_url + '?key={}'.format(self.user._id)
        )

        self.assertEqual(
            resp.status_code,
            http.NO_CONTENT
        )

    def test_delete_file_private_unauthorized(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        resp = self.app.delete(
            file_url + '?key={}'.format(self.second_user._id)
        )

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_delete_file_private_anonymous(self):

        repo_url = json.loads(
            self.app.put(
                '/?key=' + self.user._id
            ).data
        ).get('url')

        file_url = json.loads(
            self.app.put(
                repo_url + 'foo.txt?key={}'.format(self.user._id),
                data={'file': self._fake_file()}
            ).data
        )['url']

        resp = self.app.delete(file_url)

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )