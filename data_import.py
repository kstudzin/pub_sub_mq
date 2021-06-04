import csv
import fnmatch
import os
import random
from pathlib import Path


class Topics:
    TOPICS_ONE_WORD = ["Lorem", "finibus", "sodales", "tristique", "Curabitur", "consectetur"]
    TOPICS_TWO_WORD = ["consectetur adipiscing", "pellentesque dapibus", "eleifend quam", "Donec dignissim",
                       "faucibus imperdiet", "Vestibulum placerat", "aliquam interdum"]
    TOPICS_THREE_WORD = ["Nunc commodo vulputate", "eleifend quam pellentesque", "in eros aliquam",
                         "at ultricies turpis", "nibh finibus dapibus", "faucibus imperdiet erat"]
    TOPICS_FOUR_WORD = ["Suspendisse ut cursus mauris", "nulla orci blandit dolor", "tristique risus in eros",
                        "Sed consectetur eu felis", "ut blandit tortor molestie"]
    TOPICS_FIVE_WORD = ["Donec sed diam nec quam", "lobortis eleifend quam pellentesque dapibus",
                        "Sed feugiat tellus placerat justo", "Donec sodales neque quis urna",
                        "lobortis eleifend quam pellentesque dapibus", "Aliquam convallis lorem sed turpis",
                        "Sed venenatis augue eget egestas"]


class DataImport:
    def __init__(self, sample_size="short"):
        """
        Finds directory base upon sample size
        :param sample_size: short, medium, long
        """
        project_directory = Path(__file__).parent
        self.data_directory = os.path.join(project_directory, f"sampledata/{sample_size}/")
        self.sample_data = []

    def get_data(self, suffix="1") -> []:
        """
        :param suffix: sample file name index number sample is 1-5
        :return: list of dictionaries created from CSV
        """
        for file in os.scandir(self.data_directory):
            if fnmatch.fnmatch(file, f'*{suffix}.csv') and file.is_file():
                print(file.path)
                with open(file.path, 'r') as data:
                    for line in csv.DictReader(data):
                        self.sample_data.append(line)
        return self.sample_data


def main():
    data_import = DataImport("short")
    data = data_import.get_data("2")
    print(data)
    row = data[random.randrange(0, len(data))]
    keys = list(row.keys())
    key = keys[random.randrange(0, len(keys))]
    value = row[key]
    print(f"{key}: {value}")


if __name__ == "__main__":
    main()
