
import wikitextparser as wtp
from table import RadioTable, TableError
import logging

class PageError(Exception):
    __module__ = "PageInfo"

class PageInfo:
    """
    Controller for each wikipedia page. Retrieve
    needed information about a specific page type.

    A page can be:
    - a radio page
    - a list of radio
    """
    REMOVED_SECTION = [
            "see also",
            "references",
            "external links",
            ]

    RADIO = 1
    LIST = 0
    def __init__(self, page):
        self._page = page
        self.ast = wtp.parse(self._page.data['wikitext'])

        #Detect radio pages by searching a radio infobox
        self.infobox = self.radio_site = None
        self.find_infobox()
        if self.infobox:
            self.type = PageInfo.RADIO
            return None

        #Detect page with lists of radios
        #Retrieve all section delimited with an h2
        self.sections = [section for section in self.ast.sections \
            if section.level in [0, 2] and self.allowed_section(section)]

        #Get at least one table with radio listed
        self.manage_datatype("table")
        if not self.have_table:
            self.manage_datatype("list")

        if self.have_table:
            self.type = PageInfo.LIST
            return None

    def manage_datatype(self, type_data):
        """
        Try to retrieve table or list in a page. Group founded element
        in : 
         - self.tables_by_section => dict of tables grouped by section
         - self.tables => list of all tables
        """
        #Try to retrieve table for each section in the current page
        self.tables_by_section = {}
        for section in self.sections:
            self.tables_by_section.update(\
                    self.retrieve_data(section, mode=type_data))

        def group_table(section_dict):
            """
            Group all RadioTable of different section in a single list.
            Recusively search RadioTable in subsections.
            """
            list_table = []
            for section_content in section_dict.values():
                if type(section_content) == dict:
                    list_table.extend(group_table(section_content))
                elif type(section_content) == RadioTable:
                    list_table.append(section_content)
            return list_table

        self.tables = group_table(self.tables_by_section)

    def retrieve_data(self, section, mode="table"):
        """
        Recursive search to retrieve a table or list for a section,
        or existing subsection.

        Available mode : table/list

        Those element are expected to not have any sub-section, and
        different section level are stored in dict like :

        {
            "section" : {
                "sub section" : RadioTable,
                "sub section" : {
                    "sub section" : RadioTable,
                    ...
                },
                ...
            },
            "section" : RadioTable,
            ...
        }
        """
        #Retrieve default section name, set
        #page title for section without title (level 0)
        if section.title:
            title = section.title
        else:
            title = self._page.data['title']
        title = title.lower()

        #Try to retrieve subsection, with higher level
        sub_section = [sub_section for sub_section in
                section.sections if sub_section.level == section.level + 1]
        table = None

        #Search subsection table/list recursively
        if sub_section:
            args = (
                    sub_section,
                    [mode] * len(sub_section)
                    )
            list_table = list(map(self.retrieve_data, *args))
            return {title : list_table}

        #Section withou sub section, try to find table or list
        #depending of the mode.
        if mode == "table" and section.tables:
            radios_element = section.tables[0]
        elif mode == "list" and section.get_lists():
            radios_element = section.get_lists()[0].items
        #No information found in the current section
        else:
            return {title : None}

        #Convert list or table in RadioTable element
        try:
            table = RadioTable(**{mode:radios_element})
        except TableError as error:
            logging.error(error)
        return {title : table}


    @property
    def have_table(self):
        return len(self.tables) > 0

    @property
    def id(self):
        return self._page.data["pageid"]

    def allowed_section(self, section):
        """
        Remove default section of a wikipedia page,
        as listed in REMOVED_SECTION.
        """
        if section.level == 0:
            return True
        return section.title.strip().lower() not in self.REMOVED_SECTION


    def find_infobox(self):
        """
        Try to retrieve a 'radio station infobox' in
        a page, which mean it's a radio page.
        """
        for template in self.ast.templates:
            template_name = template.normal_name().lower()
            if template_name == "infobox radio station":
                self.infobox = template
        if not self.infobox:
            return None
        for argument in self.infobox.arguments:
            if argument.name.strip() == "website":
                self.radio_site = self.get_infobox_url(argument.value)

    def get_infobox_url(self, website_field):
        """
        Retrieve a website field from a radio infobox.
        Behave depending of the external link construction.
        Can be :
          - An external link to a website
          - A wikidata link
        """
        website_field = website_field.strip()
        tokenized_field = wtp.parse(website_field)
        url = None

        if tokenized_field.templates:
            template = tokenized_field.templates[0]
            template_name = template.normal_name().lower()

            # Directly an external url
            if template_name == 'url':
                url = template.arguments[0].value
            # Getting link to wikidata
            elif template_name == "official url":
                url = self._retrieve_official_website(template_name)
        #Stored as external link : "[http://www.waao.com/ waao.com]"
        elif tokenized_field.external_links:
            url = tokenized_field.external_links[0].url
        if url is not None:
            return url
        raise PageError(f"Url not found with {website_field}")


    def _retrieve_official_website(self, template_name):
        """
        Retrieve official website links from an infobox where
        this information is stored in radio template with
        website = {{Official URL}}.

        Retrieve exact claim id from wikidata.
        """
        website_labels = ["official url", "official website"]
        labels = {value:key for key, value in \
                self._page.data["labels"].items()}

        item_id = None
        index = 0
        while item_id == None and index < len(website_labels):
            item_id = labels.get(website_labels[index], None)
            index += 1
        if item_id is None:
            return None
        return self._page.data['claims'][item_id][0]
