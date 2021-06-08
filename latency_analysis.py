import os
import pathlib
import re

import pandas as pd
from matplotlib import pyplot as plt

source = "latency"
filename_pattern = re.compile(".*(sub-(\\d+)_broker-([rd])).*")
output = "boxplot.png"


def import_data():
    df = pd.DataFrame()
    names = []
    for file in os.listdir(source):
        match = filename_pattern.match(file)
        name = "{0:03}_{1}".format(int(match.group(2)), match.group(3))
        df_curr = pd.read_csv(os.path.join(source, file), header=None, usecols=[0], names=[name])
        df[name] = df_curr[name]
        names.append(name)

    names.sort()
    return df, names


def main():
    df, cols = import_data()

    plt.figure()
    df.boxplot(column=cols)
    plt.savefig(output, format="png")

    print(f"Generating plot: {output}")


if __name__ == "__main__":
    main()
