#!/usr/bin/env python3

from scanner.logger import LogRadio
from scanner.site import Site
from wikipedia.controller import SearchController
from argparse import ArgumentParser
import os

import sys

VERBOSE = None


class WorkingDirectory:
    def __init__(self, directory):
        if not os.path.exists(directory):
            os.mkdir(directory)

        self.origin = os.getcwd()
        self.workdir = os.path.join(self.origin, directory)

    def __enter__(self):
        os.chdir(self.workdir)
        return self

    def __exit__(self, *args, **kwargs):
        os.chdir(self.origin)

def get_options():
    """
    Syntax: [-h] [--wiki-title title | --csv filename] 
        [--verbose]

    See --help for options details.
    """
    global VERBOSE
    description = """
Search radio contact in list of station,
using wikipedia "list of radio stations" pages.
Retrieve radio websites available in wikipedia,
and parse them to find contact email."""

    parser = ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--wiki-title", metavar="title",
            help="Wikipedia page with radio stations list")
    group.add_argument("--csv", metavar="filename",
            help="csv file of radio list")

    parser.add_argument("-v", "--verbose",
            action="store_true", default=False)
    parser.add_argument("-w", "--workdir",
            default="scanner-search", metavar="dir",
            help="Parser working directory")

    args = parser.parse_args()

    #Error if no argument is given
    if not args.wiki_title and not args.csv:
        parser.print_usage()
        exit(f"{sys.argv[0]}: error: no argument is given")
    VERBOSE = args.verbose
    return parser.parse_args()

def parse_radio_file(wikilist_file):
    """
    Parse csv file containing radio listing, and retrieve
    contact email on radios' website.
    """
    #Prepare record file
    log_file = LogRadio(wikilist_file)
    for section in log_file.radio_dataset:

        #Go through each radio of a section, and explore radio site
        for radio_info in log_file.radio_dataset[section]:
            site = Site(radio_info.site)
            site.find_mail()
            radio_info.update_mails(site.domain_mails, site.unsure_mails)

        #Save at each explored section
        log_file.save()

def parse_wiki_list(wikilist_page, workdir):
    """
    Parse wikipedia page, mainly "List of radio stations in ..."
    like page.

    For example, see wiki :
        - List of radio stations in the United Kingdom
        - Category:Lists of radio stations by country

    Search website in wiki infobox for each radio of this listing.
    Store founded website in .template (=csv format) file,
    and use parse_radio_file to explore each radio website.
    """
    silent = VERBOSE == False
    with WorkingDirectory(workdir):
        wikisearch = SearchController(wikilist_page, silent=silent)
        wikisearch.launch()
        parse_radio_file(wikisearch.filename)

if __name__ == "__main__":
    ARGS = get_options()
    if ARGS.wiki_title:
        parse_wiki_list(ARGS.wiki_title, ARGS.workdir)
    elif ARGS.csv:
        parse_radio_file(ARGS.csv)

