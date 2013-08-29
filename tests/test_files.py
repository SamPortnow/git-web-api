from flask import json
import httplib as http
from StringIO import StringIO

from tests import GWATestCase


class FileTests(GWATestCase):

    def _make_repo(self):
        return json.loads(self.app.put('/').data).get('url')

    def _fake_file(self, contents=None, filename=None):
        return StringIO('my file contents'), 'test.txt'

    def test_add_file_no_payload(self):
        """ A PUT request without a file attached should return a 400
        """
        repo_url = self._make_repo()

        resp = self.app.put(repo_url + 'foo.txt')

        self.assertEqual(
            resp.status_code,
            http.BAD_REQUEST,
        )

    def test_add_file_success(self):
        repo_url = self._make_repo()

        resp = self.app.put(
            repo_url + 'foo.txt',
            data={
                'file': self._fake_file()
            }
        )

        self.assertEqual(
            resp.status_code,
            http.OK,
        )

    def test_get_file_not_found(self):
        repo_url = self._make_repo()

        resp = self.app.get(repo_url + 'foo.txt')

        self.assertEqual(
            resp.status_code,
            http.NOT_FOUND,
        )

    def test_get_file_success(self):
        repo_url = self._make_repo()

        resp = self.app.put(
            repo_url + 'foo.txt',
            data={
                'file': self._fake_file()
            },
            follow_redirects=True,
        )

        self.assertEqual(
            resp.status_code,
            http.OK,
        )

    def test_get_file_content(self):
        repo_url = self._make_repo()

        resp = self.app.get(
            json.loads(
                self.app.put(
                    repo_url + 'foo.txt',
                    data={
                        'file': self._fake_file()
                    },
                ).data
            ).get('url')
        )

        self.assertIn(
            resp.data,
            'my file contents',
        )

    def test_delete_file_not_found(self):
        repo_url = self._make_repo()

        resp = self.app.delete(repo_url + 'foo.txt')

        self.assertEqual(
            resp.status_code,
            http.NOT_FOUND,
        )

    def test_delete_file_success(self):
        repo_url = self._make_repo()

        self.app.put(
            repo_url + 'foo.txt',
            data={
                'file': self._fake_file()
            }
        )

        resp = self.app.delete(repo_url + 'foo.txt')

        self.assertEqual(
            resp.status_code,
            http.OK
        )