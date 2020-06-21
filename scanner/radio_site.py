import requests
import urllib.parse as URLParse
import os.path
import re

from .errors import UrlException
from .link import LinkParser

MAIL_REGEX = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
MAIL_REGEX = re.compile(MAIL_REGEX)


def is_url(parsed_url):
    """ Check if the given string is an url """
    return all([parsed_url.scheme, parsed_url.netloc])

def retrieve_email(html_content):
    """
    Find all emails within an html page.
    """
    return set(MAIL_REGEX.findall(html_content))

class Site:
    def __init__(self, url):
        self.base_url = None
        self.navigated_url = set()
        self.to_navigate_url = None
        self.list_mails = set()
        self.get_base_url(url)

        self.to_navigate_url = {self.base_url.geturl()}

    def get_base_url(self, url):
        """ Prepare the host url to get the root folder /."""
        parsed_url = URLParse.urlparse(url)
        url_params = {
            "scheme" : parsed_url.scheme,
            "netloc" : parsed_url.netloc,
            "path" : parsed_url.path,
            "query" : "",
            "fragment" : "",
                }
        self.base_url = URLParse.SplitResult(**url_params)


    def site_loop(self):
        """ """
        print("Parse : ", self.base_url.geturl())
        while True:
            try:
                url = self.to_navigate_url.pop()
            except KeyError:
                break
            try:
                content = self.parse_url(url)
            except UrlException as Error:
                continue
            mails = retrieve_email(content)
            if len(mails):
                self.list_mails |= mails
            links = self.manage_links(content)
            self.to_navigate_url |= links
        

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

    @staticmethod
    def parse_url(url):
        """
        Handler to get a website url. Control if the given
        url isn't already explored.
        """
        if url in self.navigated_url:
            continue
        self.navigated_url |= {url}
        try:
            response = requests.get(url)
        except requests.exceptions.SSLError:
            response = requests.get(url, verify=False)
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
