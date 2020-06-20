class Radio:
    def __init__(self, name, have_wiki=False):
        self.name = name
        self.have_wiki = have_wiki

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
