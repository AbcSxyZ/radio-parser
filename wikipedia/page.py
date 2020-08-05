import wikitextparser as wtp
import wptools
from .table import RadioTable
import logging
from .wiki_error import PageError, TableError, PageNotExists
from collections import OrderedDict

logger = logging.getLogger('wiki')

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
            "frequencies", #MUST BE REMOVED
            ]

    ALLOWED_INFOBOX = [
            "radio station",
            "infobox radio station",
            "infobox broadcasting network",
            ]

    RADIO = 1
    LIST = 0

    def __init__(self, title, lang, silent=False):
        self.title = title
        #Fetch page from wikipedia
        try:
            self._page = wptools.page(title, silent=silent, lang=lang).get()
            logger.info("Wiki parse {}".format(self.url))
        except LookupError:
            err_msg = f"\"{title}\" not found"
            logger.warning(err_msg)
            raise PageNotExists(err_msg)

        self.ast = wtp.parse(self._page.data['wikitext'])
        self.type = None

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
        self.manage_datatype()

        if self.have_table:
            self.type = PageInfo.LIST
            return None

        err_msg = "{} : Invalid url, not a radio station or listing"
        raise PageError(err_msg.format(self.url))

    def manage_datatype(self):
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
                    self.retrieve_data(section))

        def group_table(section_dict):
            """
            Group all RadioTable of different section in a single list.
            Recusively search RadioTable in subsections.
            """
            list_table = []
            for section_content in section_dict.values():
                if type(section_content) == OrderedDict:
                    list_table.extend(group_table(section_content))
                elif type(section_content) == list:
                    list_table.extend(section_content)
            return list_table

        self.tables = group_table(self.tables_by_section)

    def _find_section_title(self, section):
        """
        Define a section name to use for dict, using page title
        for empty title (wikitext header level 0).
        """
        if section.title:
            section_title_wikitext = wtp.parse(section.title)
            if section_title_wikitext.wikilinks:
                title = section_title_wikitext.wikilinks[0].title
            else:
                title = section.title
        else:
            title = self._page.data['title']
        return title.strip()


    def retrieve_data(self, section):
        """
        Recursive search to retrieve a table or list of a section,
        or existing subsection.

        Element from sections are stored in a dict like :

        {
            "section" : {
                "sub section" : [RadioTable, RadioTable, ...],
                "sub section" : {
                    "sub section" : [...],
                    ...
                },
                ...
            },
            "section" : [RadioTable],
            ...
        }
        """
        title = self._find_section_title(section)

        #Try to retrieve subsection, with higher level
        sub_section = [sub_section for sub_section in
                section.sections if sub_section.level == section.level + 1]

        #Search subsection table/list recursively
        if sub_section:
            sections_titles = [self._find_section_title(ast) for \
                    ast in sub_section]
            subsection_data = list(map(self.retrieve_data, sub_section))
            list_table = OrderedDict()
            for sub_section_result in subsection_data:
                list_table.update(sub_section_result)
            return OrderedDict({title : list_table})

        #Section without sub section, retrieve all
        #table and list of the wikitext
        radios_tables = []
        if  section.tables:
            radios_tables.extend(section.tables)
        if section.get_lists():
            section_lists = section.get_lists()
            radios_tables.extend([radio.items for \
                    radio in section_lists])
        #No information found in the current section
        if not radios_tables:
            return OrderedDict({title : None})

        #Convert list or table in RadioTable element
        section_tables = []
        for table in radios_tables:
            try:
                section_tables.append(RadioTable(table))
            except TableError as error:
                err_msg = f"{self.url} : {error}"
                logger.warning(err_msg)
        return OrderedDict({title : section_tables})

    @property
    def url(self):
        return self._page.data['url']

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
            if template_name in self.ALLOWED_INFOBOX:
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
        if url:
            return url

        err_msg = "Url not found with {}".format(website_field)
        raise PageError(err_msg)

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
