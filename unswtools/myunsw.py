
import os.path
import time

from unswtools import adfs


CACHE_DIRECTORY = 'cache'


def login(credentials=None):
    driver, session = adfs.session(credentials, adfs.MYUNSW)
    return driver, session


search_target_url = ("https://my.unsw.edu.au"
                     "/academic/serviceCentre/personSearch.xml"
                     "?bsdsSubmit-commit=Go&detailAction=statement&id=%s")

transcript_url = ("https://my.unsw.edu.au"
                  "/academic/staffTranscript/transcript.pdf")


class MyUnsw:

    def __init__(self, driver, session):
        self.driver = driver
        self.session = session

    def fetch_transcript(self, id, filename='auto', directory=None,
                         force=False, verbose=False):
        if filename == 'auto':
            if directory is None:
                directory = CACHE_DIRECTORY

            filename = os.path.join(directory, 'transcript-%s.pdf' % id)

        if not force and os.path.exists(filename):
            return filename

        # first results to initialise the cookies, session etc
        self.session.get(search_target_url % id)
        # the results page then uses js to go to a fixed URL where the
        # session information then provides the correct PDF
        transcript_response = self.session.get(transcript_url)

        if filename is not None:
            with open(filename, 'wb') as fh:
                fh.write(transcript_response.content)
            if verbose:
                print("Wrote %s" % filename)

        return filename

    @classmethod
    def login(cls, credentials=None):
        driver, session = login(credentials)
        return cls(driver, session)
