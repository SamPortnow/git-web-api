import os
import shutil
import unittest

from app import auth, create_app
from app.auth import KeyAuthContext


class TestAuthContext(auth.AuthContext):
    def __init__(self):
        self._ssh_keys = {
            'public': 'fake_public_key',
            'private': 'fake_private_key'
        }

    @property
    def ssh_private_key(self):
        return self._ssh_keys['private']

    @property
    def ssh_public_key(self):
        return self._ssh_keys['public']

    full_name = 'Test User'
    email = 'test_user@fakedomain.com'

    def can_read_repo(self, repo_id):
        return True

    def can_modify_repo(self, repo_id):
        return False

    def is_repo_admin(self, repo_id):
        return False


class GWATestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(ignore_auth=True).test_client()

        self.admin_user = KeyAuthContext()
        self.admin_user.can_provision = True
        self.admin_user.can_create_repos = True
        self.admin_user.save()

        self.user = KeyAuthContext()
        self.user.can_create_repos = True
        self.user.save()

    def tearDown(self):
        shutil.rmtree('/tmp/test')
        os.remove('db_foo.pkl')
        os.mkdir('/tmp/test')