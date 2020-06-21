class RadioCell:
    def __init__(self, name, have_wiki=False):
        self.name = name
        self.have_wiki = have_wiki
        self.url = None

    @property
    def has_url(self):
        if self.url is None:
            return False
        return self.url.strip() != ""

    def format(self):
        return [self.name, self.url]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
