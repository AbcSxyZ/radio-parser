import wikitextparser as wtp
from .radio_cell import RadioCell
from .wiki_error import TableError


class RadioTable:
    """
    Manage information about a wikipedia table who contain
    radio names.
    Control which column is the radio list, and store those
    links.
    """
    AVAILABLE_TAG = [
            "station name or names",
            "name",
            "call sign",
            "callsign",
            "station",
            "sendername",
            ]
    def __init__(self, data):
        self.radios = []
        if type(data) is not wtp.Table:
            self.radios = data
            self.link_converter()
            return None
        self.ast_table = data
        self.table = self.ast_table.data()
        self.fields = self._get_fields()
        self._radio_colname = self.get_radio_column()

        self.get_list_radio()


    def _get_fields(self):
        """
        Retrieve description row and clean up fields.
        """
        fields = self.table[0]
        fields = filter(None.__ne__, fields)
        return list(map(str.lower, fields))

    def get_radio_column(self):
        """
        Retrieve in a table the column corresponding to radio names
        and links.
        Check if the column name is the knowed tag list.
        """
        #Check if one of given tag is avaible
        for tag in self.AVAILABLE_TAG:
            if tag in self.fields:
                return tag
        err_msg = "No radio column in the table : {}"
        raise TableError(err_msg.format(self.fields))

    def get_list_radio(self):
        """
        Create a list with all available radios from a single table.
        """
        #Get the index on radio in the table, to keep a list of name
        index_radio = self.fields.index(self._radio_colname)

        #Retrieve in the indexed column radio names
        for row in self.table[1:]:
            radio_name = row[index_radio]
            #Remove radio without name
            if radio_name.strip() != "":
                self.radios.append(radio_name)
        self.link_converter()

    def link_converter(self):
        """
        Convert wikitext of radio name into a RadioCell element.
        Check if a link is available to the given radio.
        """
        for index, radio_field in enumerate(self.radios):
            radio_field = wtp.parse(radio_field)
            have_wiki = True if radio_field.wikilinks else False
            if have_wiki:
                radio_name = radio_field.wikilinks[0].title
            else:
                radio_name = str(radio_field)

            #replace raw wikitext by a RadioCell element
            self.radios[index] = RadioCell(radio_name, have_wiki)

    def __str__(self):
        return " | ".join(map(str, self.radios))

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        self._iter_index = iter(self.radios)
        return self

    def __next__(self):
        return next(self._iter_index)
