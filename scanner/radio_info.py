class RadioInfo:
    """
    Group all information about a single radio.
    """
    def __init__(self, name, site, domain_mails=None, unsure_mails=None):
        self.site = site.strip()
        self.name = name.strip()
        self.domain_mails = self.mails_setter(domain_mails)
        self.unsure_mails = self.mails_setter(unsure_mails)

    def __repr__(self):
        return f"{self.name}"

    def mails_setter(self, value):
        """
        Setter for any mail list. Convert a new value
        in a valid set. Split mails string separated by coma.
        """
        #Store list of mails separted by coma.
        if type(value) == str and len(value.strip()):
            value = {mail.strip() for mail in value.split(',')}
        return value if type(value) == set else set()

    def update_mails(self, domain_mails=None, unsure_mails=None):
        """Add extra mail to currents mail sets"""
        if domain_mails:
            self.domain_mails |= self.mails_setter(domain_mails)
        elif unsure_mails:
            self.unsure_mails |= self.mails_setter(unsure_mails)

    def as_csv(self):
        """
        Format single row of csv file with radio informations.
        """
        domain_str = ", ".join(self.domain_mails)
        unsure_str = ", ".join(self.unsure_mails)
        return [self.name, self.site, domain_str, unsure_str]

    @property
    def have_mail(self):
        return any([self.domain_mails, self.unsure_mails])
