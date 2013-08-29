import httplib as http

from tests import GWATestCase


class RepositoryTests(GWATestCase):

    def test_empty_repo_list(self):
        resp = self.app.get('/')

        self.assertEqual(
            resp.data,
            http.NOT_FOUND,
        )
