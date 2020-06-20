import wikitextparser as wtp
from radio import Radio

class TableError(Exception):
    __module__ = "RadioTable"
    def __init__(self, msg, *args, **kwargs):
        msg = "{}:{}".format(self.__module__, msg)
        super().__init__(msg, *args, **kwargs)

class RadioTable:
    """
    Manage information about a wikipedia table who contain
    radio names.
    Control which column is the radio list, and store those
    links.
    """
    AVAILABLE_TAG = ["name", "call sign"]
    def __init__(self, table):
        self.radios = []
        self.ast_table = table
        self.table = table.data()
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
        Using Radio object for interfacig a single radio station.
        """
        #Get the index on radio in the table, and keep a list of name
        index_radio = self.fields.index(self._radio_colname)
        list_radio = [row[index_radio] for row in self.table[1:]]

        #Create Radio object for each table cell
        for radio_cell in list_radio:
            radio_cell = wtp.parse(radio_cell)
            have_wiki = False
            if radio_cell.wikilinks:
                have_wiki = True
                radio_name = radio_cell.wikilinks[0].title
            else:
                have_wiki = False
                radio_name = str(radio_cell)

            #Fill our radio list contained by a RadioTable.
            self.radios.append(Radio(radio_name, have_wiki))

