from flask import json
import httplib as http
from unittest import skip

from tests import GWATestCase


class RepositoryTests(GWATestCase):

    def test_repo_list_empty(self):
        """ Before the user creates a repository, the list of repositories
        should be empty.
        """
        resp = self.app.get('/')

        self.assertEqual(
            json.loads(resp.data),
            { 'repos': [] },
        )

    def test_repo_list(self):
        """ After creating a repo, a list of length 1 should be returned """
        self.app.put(
            '/',
            data={'public': 1}
        )

        resp = self.app.get('/')

        self.assertEqual(
            len(json.loads(resp.data)['repos']),
            1
        )

    def test_create_repository(self):
        """ Create a new repository"""

        resp = self.app.put('/')

        self.assertEqual(
            resp.status_code,
            http.OK,
        )

        # { 'url': '...' }
        self.assertIsNotNone( json.loads(resp.data).get('url') )

    def test_created_repository_is_valid(self):
        """ Create a repository; the URL (GET) should return HTTP 200 """
        resp = self.app.get(
            json.loads(
                self.app.put('/').data
            ).get('url')
        )

        self.assertEqual(
            resp.status_code,
            http.OK,
        )

    def test_repository_not_found(self):
        """ HTTP 404 should be returned for a repository that doesn't exist """
        resp = self.app.get('/not_a_repo/')

        self.assertEqual(
            resp.status_code,
            http.NOT_FOUND,
        )