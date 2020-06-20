#!/usr/bin/env python3

import mwclient
import wptools
import wikitextparser as wtp
import logging
from page import PageInfo

logging.basicConfig(filename="radio_json.log")

class PageNotExists(ValueError):
    __module__ = "WikiSearch"

class WikiSearch:
    SITE = "en.wikipedia.org"
    def __init__(self):
        self.client = mwclient.Site(self.SITE)

    def search(self, title):
        # print(self.client.pages[title])
        # import code
        # code.interact(local=locals())
        try:
            page = wptools.page(title, wiki="en.wikipedia.org").get()
        except LookupError:
            raise PageNotExists("\"{}\" not found.".format(title))

        parsed_page = PageInfo(page, self.client)
        # import code
        # code.interact(local=locals())
        return parsed_page


if __name__ == "__main__":
    wikipedia = WikiSearch()
    # page = wikipedia.search("List of radio stations in the United Kingdom")
    # page = wikipedia.search("Category:Lists_of_radio_stations_in_the_United_States")

    # page = wikipedia.search("BBC Asian Network")
    # page = wikipedia.search("Classic_FM_(UK)")
    import sys
    title = sys.argv[1]
    page = wikipedia.search(title)
    print(page.infobox)
    print(page.radio_site)
    # page = wikipedia.search("List of radio stations in Alabama")
    # page = wikipedia.search("List of radio stations in Belgium")
    # print(page.text())
    # page = wikipedia.search("blfrafqa")
    pass



