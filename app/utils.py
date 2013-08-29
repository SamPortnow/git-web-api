from string import ascii_lowercase
from random import randint


def new_repo_name(length=5):
    return ''.join(
        [
            ascii_lowercase[randint(0,len(ascii_lowercase) -1)]
            for _ in xrange(length)
        ]
    )