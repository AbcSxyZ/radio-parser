class ScannerError(Exception):
    """Base for module exceptions"""

class UrlException(ScannerError):
    """Raise when there is an error while trying to GET url"""
    __module__ = "Site"

class LifetimeExceeded(ScannerError):
    """Site parsing exceeded the limited time"""
    __module__ = "Site"
