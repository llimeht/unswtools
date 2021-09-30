from unswtools import adfs
from moodletools import moodle

url = "https://moodle.telt.unsw.edu.au/"


def login(credentials=None):
    driver, session = adfs.session(credentials, adfs.MOODLE)

    m = moodle.Moodle(url, session)

    return m
