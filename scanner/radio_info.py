class RadioInfo:
    """
    Group all information about a single radio.
    """
    def __init__(self, name, site, domain_mails=set(), unsure_mails=set()):
        self.site = site.strip()
        self.name = name.strip()
        self.domain_mails = self.mails_setter(domain_mails)
        self.unsure_mails = self.mails_setter(unsure_mails)

    def __repr__(self):
        return f"{self.name}"

    def mails_setter(self, value):
        if type(value) == str:
            if len(value.strip()) == 0:
                value = {}
            else:
                value = {mail.strip() for mail in value.split(',')}
        return value

    def update_mails(self, domain_mails=None, unsure_mails=None):
        if domain_mails:
            self.domain_mails |= self.mails_setter(domain_mails)
        elif unsure_mails:
            self.unsure_mails |= self.mails_setter(unsure_mails)

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
        """
        Format single row of csv file with radio informations.
        """
        domain_mails_str = ", ".join(self.domain_mails)
        unsure_mails_str = ", ".join(self.unsure_mails)
        mails = (domain_mails_str, unsure_mails_str)
        return [self.name, self.site, *mails]

    @property
    def have_mail(self):
        return any([self.domain_mails, self.unsure_mails])
