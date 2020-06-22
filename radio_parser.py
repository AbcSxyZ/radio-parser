#!/usr/bin/env python3

from scanner.logger import LogRadio
from scanner.site import Site
from wikipedia.controller import SearchController
from argparse import ArgumentParser

import sys
def get_options():
    """

    """
    description = """Search radio email in wikipedia list of radio station.
Retrieve a radio's website in wikipedia, and parse the website
to find email."""

    parser = ArgumentParser(description=description)
    parser.add_argument('wikilist', type=str, nargs=1)
    return parser.parse_args()


def main(ARGS):
    wikisearch = SearchController(ARGS.wikilist[0], silent=False)
    print(wikisearch.filename)
    wikisearch.launch()
    log_file = LogRadio(wikisearch.filename)
    for section in log_file.radio_dataset:
        for radio in log_file.radio_dataset[section]:
            site = Site(radio.site)
            site.find_mail()
            radio.update_mails(site.domain_mails, site.unsure_mails)
    log_file.save()
    

if __name__ == "__main__":
    ARGS = get_options()
    
    if len(sys.argv) == 2:
        main(ARGS)

