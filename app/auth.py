# Use permanent API keys to associate abstract users with credentials.

# Where are author and email stored?

# This side - how can we subscribe to changes on the source system?

# Client site - what are the implications of trusting them?


class AuthContext(object):
    def __init__(self,
                 ssh_key_pair=None,
                 full_name=None,
                 email=None):
        """Create a User with the passed settings. If settings are not passed,
        get them from the current context.
        """
        pass

    @property
    def ssh_private_key(self):
        raise NotImplementedError

    @property
    def ssh_public_key(self):
        raise NotImplementedError

    @property
    def full_name(self):
        raise NotImplementedError

    @property
    def email(self):
        raise NotImplementedError

    def can_read_repo(self, repo_id):
        raise NotImplementedError

    def can_modify_repo(self, repo_id):
        raise NotImplementedError

    def is_repo_admin(self, repo_id):
        raise NotImplementedError


def get_auth_context():
    """ Return an instance of a descendant of AuthContext.
    """
    # TODO: Make this work :)
    from .tests import TestAuthContext
    return TestAuthContext()