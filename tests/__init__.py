import os
import shutil
import unittest

from app import create_app
from app.auth import KeyAuthContext


class GWATestCase(unittest.TestCase):
    git_root = '/tmp/test/'

    def setUp(self):
        self.app = create_app(
            ignore_auth=True,
            git_root=self.git_root
        ).test_client()

        self.admin_user = KeyAuthContext()
        self.admin_user.can_provision = True
        self.admin_user.can_create_repos = True
        self.admin_user.save()

        self.user = KeyAuthContext()
        self.user.can_create_repos = True
        self.user.save()

    def tearDown(self):
        shutil.rmtree(self.git_root)
        os.remove('db_foo.pkl')
        os.mkdir(self.git_root)