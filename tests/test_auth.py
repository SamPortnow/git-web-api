import httplib as http

from flask import json

from tests import GWATestCase
from app import create_app


class AuthTestCase(GWATestCase):
    def setUp(self):
        super(AuthTestCase, self).setUp()
        self.app = create_app().test_client()

    def test_create_repo_fail(self):
        resp = self.app.put('/')

        self.assertEqual(
            resp.status_code,
            http.UNAUTHORIZED
        )

    def test_create_repo_succeed(self):
        resp = self.app.put('/?key=' + self.user._id)

        self.assertEqual(
            resp.status_code,
            http.OK
        )

    def test_list_repo_without_access(self):
        json.loads(
            self.app.put('/?key=' + self.user._id).data
        ).get('url')

        self.assertEqual(
            json.loads(self.app.get('/').data).get('repos'),
            []
        )

    def test_list_repo_with_access(self):
        json.loads(
            self.app.put('/?key=' + self.user._id).data
        ).get('url')

        repos = json.loads(
            self.app.get('/?key=' + self.user._id).data
        ).get('repos')

        self.assertEqual(len(repos), 1)

    def test_list_repo_public(self):

        self.app.put(
            '/?key=' + self.user._id,
            data={'is_public': 1}
        )

        repos = json.loads(
            self.app.get('/').data
        ).get('repos')

        self.assertEqual(len(repos), 1)