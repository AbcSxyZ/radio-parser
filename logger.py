import csv
import threading
from collections import OrderedDict
import fcntl

class RadioInfo:
    """
    Group all information about a single radio.
    """
    def __init__(self, name, site, mails):
        self.site = site
        self.mails = mails
        self.name = name

    def __repr__(self):
        return self.name

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


class LogRadio:
    """
    Interface to manipulate the radio's csv file, containaing
    all site and emails of radios.
    """
    def __init__(self, filename):
        self.filename = filename
        self.filestream = None
        self.description_column = None
        with self:
            self.radio_dataset = self.retrieve_data()

    def retrieve_data(self):
        """
        Retrieve all logged info about radios.
        Store information in a dictionnary with format
        {
          "departement1" : [RadioInfo1, RadioInfo2, ...],
          "departement2" : [...],
          ...
        }
        """
        logfile = csv.reader(self.filestream, delimiter=';')

        #Skip first line (description row)
        self.description_column = next(logfile)

        #Go through each line of the csv
        radio_dataset = OrderedDict()
        for departement, radio, site, mails in logfile:
            #Getting row with a new departement
            if departement:
                current_departement = departement
                radio_dataset.update({departement:[]})
            #Otherwise, store radio info stored in a single row
            else:
                radio_dataset[current_departement].\
                        append(RadioInfo(radio, site, mails))
        return radio_dataset

    def update_dataset(self):
        """
        Merge current dataset in the file with
        data stored in object memory.
        """
        tmp_radio_dataset = self.retrieve_data()

        for departement in tmp_radio_dataset:
            departement_radios_old = self.radio_dataset[departement]
            departement_radios_new = tmp_radio_dataset[departement]
            for new_radio, old_radio in \
                zip(departement_radios_new, departement_radios_old):
                new_radio.merge(old_radio)

        self.radio_dataset = tmp_radio_dataset


    def update_info(self, radio, mails):
        """
        Change email list of the given radio name
        """
        for departement in self.radio_dataset.keys():
            departement_radios = self.radio_dataset[departement]
            for radio_info in departement_radios:
                if radio_info.name == radio:
                    radio_info.add_mail(mails)
        with self:
            self.update_dataset()
            self.filestream.seek(0)
            self.save()

    def __enter__(self):
        """
        Set a file lock using flock on the current file
        """
        self.filestream = open(self.filename, \
                'r+', encoding='utf8')
        fcntl.flock(self.filestream.fileno(), fcntl.LOCK_EX)
        return self.filestream

    def __exit__(self, *args, **kwargs):
        self.filestream.close()

    def save(self):
        """
        Write current self.radio_dataset in the logfile.
        """
        writer = csv.writer(self.filestream, delimiter=';')

        #Write description column
        writer.writerow(self.description_column)

        #Go through each departement followed by each radio
        #of this departement
        for departement in self.radio_dataset.keys():
            writer.writerow([departement, "", "", ""])
            for radio_info in self.radio_dataset[departement]:
                writer.writerow(radio_info.as_csv())

    def radio_list(self):
        """
        Retrieve the entire list of radio available in the logfile
        """
        list_radios = []
        for departement in self.radio_dataset:
            for radio in self.radio_dataset[departement]:
                list_radios.append(radio)
        return list_radios
