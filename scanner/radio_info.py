class RadioInfo:
    """
    Group all information about a single radio.
    """
    def __init__(self, name, site, mails=None, extra=None):
        self.site = site
        self.name = name
        self.extra = extra
        self.mails = mails

    def __repr__(self):
        return f"{self.name} - {self.site}"

    @property
    def mails(self):
        return self._mails

    @mails.setter
    def mails(self, value):
        if type(value) == str:
            if len(value.strip()) == 0:
                value = None
            else:
                value = {mail.strip() for mail in value.split(',')}
        self._mails = value

    def mails_str(self):
        """
        Format a string with all emails, separate by a coma
        """
        if self.mails is None:
            return ""
        return ", ".join(self.mails)

    def add_mail(self, mail):
        """
        Add some extra mail into the current list of mail
        """
        if type(mail) == str:
            mail = {mail}
        if type(mail) != set:
            return
        if self.mails:
            self.mails = self.mails | mail
        else:
            self.mails = mail

    def as_csv(self):
        return ['', self.name, self.site, self.mails_str()]

    def merge(self, other):
        self.add_mail(other.mails)

