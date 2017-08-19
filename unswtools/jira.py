from jira import JIRA

import unswtools.login


JIRA_URL = 'https://jira.unsw.edu.au/'


def login(credentials=None):
    """ login to the UNSW JIRA site, returning a JIRA object """

    username, password = unswtools.login.load_credentials(credentials)

    options = {
        'server': JIRA_URL,
    }
    basic_auth = (username, password)

    j = JIRA(options, basic_auth=basic_auth)

    return j
