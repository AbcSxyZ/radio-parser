import requests
from requests.exceptions import SSLError, ConnectionError
import urllib.parse as URLParse
import os.path
import re
import time

from .errors import UrlException, LifetimeExceeded
from .link import LinkParser

MAIL_REGEX = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
MAIL_REGEX = re.compile(MAIL_REGEX)

MEDIA_EXTENSIONS = ['svg', 'png', 'jpg', 'jpeg', 'mp3', 'mp4']


def is_url(parsed_url):
    """ Check if the given string is an url """
    return all([parsed_url.scheme, parsed_url.netloc])

def retrieve_email(html_content):
    """
    Find all emails within an html page.
    """
    return set(MAIL_REGEX.findall(html_content))

class Site:
    DESPERATE = 0
    NORMAL = 1
    MAX_LEVEL = 3
    MAX_UNSURE = 5
    LIFETIME = 30
    def __init__(self, url):
        self.creation = time.perf_counter()
        self.base_url = None
        self.navigated_url = set()
        self.to_navigate_url = None
        self._mails_raw = set()
        self.unsure_mails = set()
        self.domain_mails = set()
        self.mode = self.NORMAL

        self.get_base_url(url)
        self.to_navigate_url = {self.base_url.geturl()}

        self.domain = self.base_url.netloc
        if self.domain.startswith("www."):
            self.domain = self.domain.replace("www.", "", 1)

    def get_base_url(self, url):
        """ Prepare the host url to get the root folder /."""
        parsed_url = URLParse.urlparse(url)
        path = parsed_url.path if is_url(parsed_url) else ""
        netloc = parsed_url.netloc if is_url(parsed_url) else url

        url_params = {
            "scheme" : "https",
            "netloc" : netloc,
            "path" : path,
            "query" : "",
            "fragment" : "",
                }

        self.base_url = URLParse.SplitResult(**url_params)


    def site_loop(self):
        """ """
        homepage = True
        nesting_level = 0
        self._cached_url = set()
        while len(self.to_navigate_url):
            url = self.to_navigate_url.pop()
            try:
                content = self.parse_url(url)
            except (UrlException, LifetimeExceeded) as Error:
                continue

            #Store mail like element of the page
            self._mails_raw |= retrieve_email(content)

            #Try to add extra links for a research
            self._cached_url |= self.manage_links(content)

            #Go deeper into the website, starting by searching
            #all link of an homepage, all links from those links etc.
            if len(self.to_navigate_url) == 0:
                #Behave differently in DESPERATE or NORMAL mode.
                #
                #- For normal mode, parse all link of the homepage.
                #- For desperate mode, find link of link for multiple
                #level, specified by MAX_LEVEL
                if not nesting_level < self.MAX_LEVEL:
                    return
                if self.mode == Site.NORMAL and homepage == False:
                    return
                nesting_level += 1
                self.to_navigate_url = self._cached_url
                self._cached_url = set()
                homepage = False

    def find_mail(self):
        """
        Retrieve email in the html content of a website.
        Parse multiple url of the site.

        Perform a search in 2 mode : NORMAL, followed by DESPERATE.

        In NORMAL mode, search only page linked from the homepage,
        and expect to find email with related domain.

        DESPERATE mode is launched when no domain emails are founded,
        go deeper in the website, searching links of links in 
        multiple level, specified by MAX_LEVEL.

        Expect also to get domain email from DESPERATE search,
        otherwise keep some founded emails.
        """
        print("Parse : ", self.base_url.geturl())
        #Start with normal mode.
        self.site_loop()
        if self.clean_mails():
            return None

        #Change to desperate mode
        self.mode = Site.DESPERATE
        self.to_navigate_url = self._cached_url
        self.site_loop()
        self.clean_mails(save_unsure=True)


    def convert_site_url(self, url:str):
        """
        Convert an url to a ParseResult. Control
        if it's a valid link, and if it's pointing
        to the website.
        """
        parsed_url = URLParse.urlparse(url)

        #Remove image links
        extension = parsed_url.path.split('.')[-1]
        if extension.lower() in ['svg', 'png', 'jpg', 'jpeg', 'mp3', \
                'mp4']:
            return None

        #Having an entire url in href
        if is_url(parsed_url):
            if self.base_url.netloc != parsed_url.netloc:
                return None
            if parsed_url.scheme not in ["http", "https"]:
                return None
            return parsed_url

        #Having only a path or a fragment
        path = os.path.join(self.base_url.path, parsed_url.path)
        path = os.path.realpath(path)
        return self.base_url._replace(path=path)

    def parse_url(self, url):
        """
        Handler to get a website url. Control if the given
        url isn't already explored.
        """
        actual_lifetime = time.perf_counter() - self.creation
        if actual_lifetime > self.LIFETIME:
            self.to_navigate_url = set()
            self.clean_mails(save_unsure=True)
            raise LifetimeExceeded("Parsing duration under LIFETIME")

        if url in self.navigated_url:
            raise UrlException(f"'{url}' : url already navigated.")
            
        self.navigated_url |= {url}
        try:
            response = requests.get(url, timeout=5)
        except (SSLError, ConnectionError):
            try:
                response = requests.get(url, verify=False)
            except (SSLError, ConnectionError):
                raise UrlException(f"{url}: ssl error")
        if response.status_code == 200:
            return response.text
        raise UrlException("{}: invalid url".format(url))

    def manage_links(self, html_content):
        """
        Retrieve all link of a given page who is pointing
        to an other page of the site 
        """
        #Extract all link of a html page
        parser = LinkParser()
        link_list = parser.parse_links(html_content)

        #Retrieve all links related to the website
        website_links = []
        for link in link_list:
            formatted_link = self.convert_site_url(link)
            if formatted_link:
                website_links.append(formatted_link)

        return {link.geturl() for link in website_links}

    def check_domain_mails(self):
        """
        Search email attached to the website domain name.
        """
        for mail in self._mails_raw:
            user, domain = mail.split("@")
            if domain == self.domain:
                self.domain_mails |= {mail}
        return len(self.domain_mails)

    def clean_mails(self, save_unsure=False):
        self._mails_raw = {mail for mail in self._mails_raw \
                if not self.is_image(mail)}
        if not self.check_domain_mails() and save_unsure:
            self.unsure_mails = list(self._mails_raw)[:self.MAX_UNSURE]
            self.unsure_mails = set(self.unsure_mails)
        return len(self.domain_mails)

    @staticmethod
    def is_image(path):
        return path.split('.')[-1] in MEDIA_EXTENSIONS