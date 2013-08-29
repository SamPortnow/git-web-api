import unittest
from app import auth, create_app


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
        self.app = create_app().test_client()

    def tearDown(self):
        pass

    def test_nothing(self):
        pass