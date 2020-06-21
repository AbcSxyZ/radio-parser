import csv
import threading
from collections import OrderedDict
import fcntl
from .radio_info import RadioInfo


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
          "section" : [RadioInfo1, RadioInfo2, ...],
          "section" : [...],
          ...
        }
        """
        logfile = csv.reader(self.filestream, delimiter=';')

        #Skip first line (description row)
        # self.description_column = next(logfile)
        logfile = list(logfile)

        #Go through each line of the csv
        radio_dataset = OrderedDict()
        # for departement, radio, site, mails in logfile:
        for row in logfile:
            row = [cell for cell in row if len(cell.strip())]
            #Getting row with a new section
            if len(row) == 1:
                current_section = row[0]
                radio_dataset.update({current_section:[]})
            #Otherwise, store radio info stored in a single row
            else:
                radio_dataset[current_section].\
                        append(RadioInfo(*row))
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        log = LogRadio(filename)
        print(log)
        print(log.radio_dataset)
    pass
