from __future__ import unicode_literals

import os.path


def load_credentials(credentials=None):
    """ extract username and password from a text config file

    If no filename is specified, the file '.unsw_credentials' from the
    user's home directory is used.

    Format is:

        username:password

    Note: password is in PLAIN TEXT
    """
    if credentials is None:
        credentials = '~/.unsw_credentials'

    if credentials.startswith('~'):
        credentials = os.path.expanduser(credentials)

    with open(credentials) as fh:
        username, password = fh.readline().split(':', 1)

    password = password.strip()

    return username, password
