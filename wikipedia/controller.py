
from .page import PageInfo
from .radio_cell import RadioCell
from .wiki_error import PageError, PageNotExists, ControllerError
from collections import OrderedDict
import logging
import sys
import csv
import os

logger = logging.getLogger("wiki")

class SearchController:
    """
    Manage the parsing of an entire list of radio station from
    wikipedia.

    Work with a list of radio, and retrieve for each of this
    radio the website available in their own wikipage infobox.
    """
    NB_CSV_COLUMNS = 4

    def __init__(self, base_title, silent=False, base_page=None):
        self.base_title = base_title.strip()
        self.base_page = base_page
        self.silent = silent
        self.childs = []
        self.parsed = set()

        self.workdir = self._choose_filename(self.base_title)
        self.workdir = os.path.join(os.getcwd(), self.workdir)

        self.filename = self.base_title + ".csv"


    def launch(self):
        """
        Parse a wikipedia page, which is expected to be a list
        of radio station, and retrieve all radio wikipedia pages
        linked within this list.

        Store founded information in the selected way.
        """
        if not self.base_page:
            self.base_page = self._search_page(self.base_title, False)

        if self.base_page.type != PageInfo.LIST:
            err_msg = "'{}' not a page of radio listing."
            raise ControllerError(err_msg.format(self.base_title))

        logger.info(f"Controller begin with : '{self.base_title}'")
        #Generator, will allow saving between each table parsing.
        for table in self._search_tables():
            self.save()

    def _search_page(self, title, catch=True):
        """
        Layer to perform the seach a of wiki page.
        
        Control explored urls with self.parsed to avoid
        getting mutliple time the same page.

        Control errors of expected page.

        return: None or the corresponding PageInfo.
        """
        page = None
        title = str(title)

        #Avoid asking multiple time the same page.
        if title in self.parsed:
            return None
        self.parsed |= {title}

        #Retrieve wikipedia page, manage errors.
        try:
            page = PageInfo(title, silent=self.silent)
        except (PageError, ValueError) as Error:
            logger.warning(Error)
            if catch == False:
                raise Error
        return page

    def _search_tables(self):
        """
        Research individual radio wiki page 
        in all tables of the base_page.
        """
        for radios_table in self.base_page.tables:
            #Remove table's radios without wiki.
            radio_with_wiki = filter(lambda radio:radio.have_wiki,
                    radios_table)

            #Research radio wiki
            for radio in radio_with_wiki:
                wiki_page = self._search_page(radio)
                if wiki_page is None:
                    continue

                #Store radio url if it's a radio page.
                if wiki_page.type == PageInfo.RADIO:
                    radio.url = wiki_page.radio_site
                #Create new controller for a wiki with radio listing.
                elif wiki_page.type == PageInfo.LIST:
                    new_control = SearchController(str(radio), base_page=wiki_page)
                    self.childs.append(new_control)

            #Stop at each table, to perform saving.
            yield radios_table

    def save(self):
        """
        Write in csv file all parsed informations.
        """
        self.rm()
        self._save_sections(self.base_page.tables_by_section)

    def rm(self):
        """
        Remove csv file related to the controller.
        """
        if os.path.exists(self.filename):
            os.unlink(self.filename)

    @staticmethod
    def _allow_radio_save(radio_search):
        """
        Controller to verify if a radio element must be saved.
        """
        if radio_search.has_url:
            return True
        return False

    def _save_sections(self, section_dict, parent_section=[]):
        """
        Recursive save of each sections of a page.
        Save each list of table for each section/subsection dict.
        """
        for section_title in section_dict.keys():
            subsection_base = parent_section + [section_title]
            section_content = section_dict[section_title]
            if type(section_content) == list:
                self._save_tables(section_content, subsection_base)
            elif type(section_content) == OrderedDict:
                self._save_sections(section_content, subsection_base)

    def _save_tables(self, section_tables, parent_section):
        """
        Save single list of RadioTable. Write a row in self.filename
        for each radio field.
        """
        section_name = "/".join(parent_section)
        title_printed = False
        for table in section_tables:
            for radio in filter(self._allow_radio_save, table):
                #Display section title on first print
                if title_printed == False:
                    self._write_row([section_name])
                    title_printed = True

                #Format a radio row and write it to self.filename
                field = radio.format() # NEEDED
                self._write_row(field)

    def _write_row(self, row):
        """
        Write single row at the end of the attached csv file.
        """
        row = row + [""] * (self.NB_CSV_COLUMNS - len(row))
        with open(self.filename, 'a', encoding="utf8") as datafile:
            writer = csv.writer(datafile, delimiter=";")
            writer.writerow(row)

    def _choose_filename(self, filename):
        """
        Select the controller filename, depending
        if the given filename already exists or not.

        If the filename exists, add index extension
        to the name.
        """
        if not os.path.exists(filename):
            return filename
        index = 0
        while True:
            new_filename = f"{filename}.{index}"
            if not os.path.exists(new_filename):
                return new_filename
            index += 1

    def __enter__(self):
        """
        Move to a specifc working directory
        """
        self._old_pwd = os.getcwd()
        os.mkdir(self.workdir)
        os.chdir(self.workdir)
        return self

    def __exit__(self, *args, **kwargs):
        os.chdir(self._old_pwd)
        return None
