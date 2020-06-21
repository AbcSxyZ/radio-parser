class ScannerError(Exception):
    """Base for module exceptions"""

class UrlException(ScannerError):
    """Raise when there is an error while trying to GET url"""

