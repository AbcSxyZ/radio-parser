
import logging

class WikipediaRadioError(Exception):
    """ Base class for module exception """
    __module__ = "WikiSearch"

class PageError(WikipediaRadioError):
    __module__ = "Page"

class TableError(WikipediaRadioError):
    """
    Related error to table creation, during parsing
    wikipedia data.
    """
    __module__ = "RadioTable"

class PageNotExists(PageError):
    """ The wikipedia page expected do not exists. """
    __module__ = "Page"

class DuplicateSearch(PageError):
    """
    Try to perform a search multiple time on the same wikipedia page
    """
    __module__ = "Page"

