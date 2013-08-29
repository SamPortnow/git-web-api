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
            http.FOUND,
        )

    def test_add_file_redirect(self):
        repo_url = self._make_repo()

        resp = self.app.put(
            repo_url + 'foo.txt',
            data={
                'file': self._fake_file()
            }
        )

        self.assertIn(
            repo_url + 'foo.txt',
            resp.location,
        )