import time
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from unswtools.login import load_credentials

# TODO look at https://github.com/jaraco/keyring for username/password

MOODLE = "https://moodle.telt.unsw.edu.au/auth/oidc/"
MYUNSW = r"https://sso.unsw.edu.au/cas/clientredirect?client_name=azuread&service=https%3A%2F%2Fmy.unsw.edu.au%2Fportal%2FadfAuthentication&locale=en"

DEFAULT_DOMAIN = "ad.unsw.edu.au"

# FIXME: this should be an option somewhere and use some standard XDG dirs somehow?
PROFILE_DIR = "unsw-tools-selenium"

def session(credentials='~/.unsw_credentials', service=MYUNSW):

    try:
        username, password = load_credentials(credentials)
    except:
        username, password = None, None

    if username and "@" not in username:
        username = "%s@%s" % (username, DEFAULT_DOMAIN)

    return login(service, username, password)


rendering_pause = 3   # seconds
useragent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"

def login(url, username, password):
    # initialise the session and get the session cookie from SSO

    opts = Options()
    opts.add_argument(f"user-data-dir={PROFILE_DIR}")
    opts.add_argument(f"user-agent={useragent}")
    driver = webdriver.Chrome(chrome_options=opts)

    driver.get(url)
    # FIXME: this should be waitable
    time.sleep(rendering_pause) # wait for redirection and rendering

    if driver.current_url.startswith("https://login.microsoftonline.com/"):
        # haven't been auto redirected so do the login

        if username:
            driver.find_element_by_xpath("//input[@name='loginfmt']").send_keys(username)
            driver.find_element_by_xpath("//input[@type='submit']").click()
            time.sleep(rendering_pause)

            if password:
                driver.find_element_by_xpath("//input[@name='passwd']").send_keys(password)
                driver.find_element_by_xpath("//input[@type='submit']").click()
                time.sleep(rendering_pause)

                driver.find_element_by_xpath("//input[@type='submit']").click()

        else:   # FIXME this should be waitable
            input("After logging in, press ENTER to continue. ")

    session = requests.Session()
    session.cookies.update({
        c['name']: c['value']
        for c in driver.get_cookies()
    })
    session.headers.update({'User-Agent': useragent})

    return driver, session
