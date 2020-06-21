class WikipediaRadioError(Exception):
    """ Base class for module exception """
    __module__ = "WikiSearch"

class TableError(WikipediaRadioError):
    """
    Related error to table creation, during parsing
    wikipedia data.
    """
    __module__ = "WikiRadioTable"

class PageError(WikipediaRadioError):
    __module__ = "WikiPage"

class PageNotExists(PageError):
    """ The wikipedia page expected do not exists. """
    __module__ = "WikiPage"

class DuplicateSearch(PageError):
    """
    Try to perform a search multiple time on the same wikipedia page
    """
    __module__ = "WikiPage"

class ControllerError(WikipediaRadioError):
    __module__ = "WikiController"
    pass
