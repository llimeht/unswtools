from unswtools import sso
from moodletools import moodle

url = "https://moodle.telt.unsw.edu.au/"


def login(credentials):
    session = sso.session(credentials, sso.MOODLE)

    m = moodle.Moodle(url, session)

    return m
