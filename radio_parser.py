#!/usr/bin/env python3

from scanner.logger import LogRadio
from scanner.site import Site
from wikipedia.controller import SearchController
from argparse import ArgumentParser
from workdir import WorkingDirectory

VERBOSE = None

def get_options():
    """
    See --help for options details.
    """
    global VERBOSE

    description = """
Search radio contact in list of station,
using wikipedia "list of radio stations" pages.
Retrieve radio websites available in wikipedia,
and parse them to find contact email."""

    parser = ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-w", "--wiki-title", metavar="title",
            help="Wikipedia page with radio stations list")
    group.add_argument("--csv", metavar="filename",
            help="csv file of radio list")
    group.add_argument("-s", "--site", metavar="site",
            help="Search email in the given site")

    parser.add_argument("-v", "--verbose",
            action="store_true", default=False)
    parser.add_argument("--workdir",
            default="scanner-search", metavar="dir",
            help="Parser working directory")

    parser.add_argument("-l", "--lang",
            default="en", metavar="wiki-language",
            help="Select wikipedia's lang")

    args = parser.parse_args()

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

def parse_wiki_list(wikilist_page, lang, workdir):
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
        wikisearch = SearchController(wikilist_page, lang, silent=silent)
        wikisearch.launch()
        parse_radio_file(wikisearch.filename)

def parse_radio_site(url):
    """
    Retrieve emails from a single website, print them on stdout.
    """
    site = Site(url)
    site.find_mail()
    print("Domain mail : {}".format(site.domain_mails))
    print("unknow mail : {}".format(site.unsure_mails))

if __name__ == "__main__":
    ARGS = get_options()
    if ARGS.wiki_title:
        parse_wiki_list(ARGS.wiki_title, ARGS.lang, ARGS.workdir)
    elif ARGS.csv:
        parse_radio_file(ARGS.csv)
    elif ARGS.site:
        parse_radio_site(ARGS.site)

