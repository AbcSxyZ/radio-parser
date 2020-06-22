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
        self.datafile = filename
        # Replace .template extension by .csv
        filename = filename.split('.')[:-1] + ["csv"]
        self.recordfile = ".".join(filename)
        self.description_column = None
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
        with open(self.datafile, "r") as datafile:
            wikilist_data = list(csv.reader(datafile, delimiter=';'))

        #Go through each line of the csv
        radio_dataset = OrderedDict()
        for row in wikilist_data:
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

    def save(self):
        """
        Write current self.radio_dataset in the logfile.
        """
        savestream = open(self.recordfile, "w")
        writer = csv.writer(savestream, delimiter=';')

        #Go through each section followed by each radio
        #of this section
        for section in self.radio_dataset.keys():
            section_printed = False
            writer.writerow([section, "", "", ""])
            for radio_info in self.radio_dataset[section]:
                if radio_info.have_mail:
                    if section_printed == False:
                        writer.writerow([section, "", "", ""])
                        section_printed = True
                    writer.writerow(radio_info.as_csv())
        savestream.close()

    def radio_list(self):
        """
        Retrieve the entire list of radio available in the logfile
        """
        list_radios = []
        for section in self.radio_dataset:
            for radio in self.radio_dataset[section]:
                list_radios.append(radio)
        return list_radios
