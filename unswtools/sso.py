from __future__ import unicode_literals

import bs4
import os.path
import requests

from unswtools.login import load_credentials


sso_url = ('https://ssologin.unsw.edu.au/cas/login?'
           'service=%s?'
           'authCAS=CAS')

MOODLE = "https://moodle.telt.unsw.edu.au/login/index.php"
MYUNSW = "https://my.unsw.edu.au/portal/adfAuthentication"


def session(credentials='~/.unsw_credentials', service=MYUNSW):

    username, password = load_credentials(credentials)

    return login(sso_url % service, username, password)


def login(url, username, password):
    # initialise the session and get the session cookie from SSO
    sso_session = requests.Session()
    response_form = sso_session.get(url)

    # extract the magic lt variable (login token (?))
    soup = bs4.BeautifulSoup(response_form.text, "html.parser")
    form = soup.find(id='muLoginForm')
    lt = form.find('input', {'name': 'lt'})

    sso_payload = {
        '_eventId': 'submit',
        'lt': lt.get('value'),
        'submit': 'submit',
        'username': username,
        'password': password
    }

    sso_session.post(url, data=sso_payload)
    return sso_session
