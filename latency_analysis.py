import os
import pathlib
import re

import pandas as pd
from matplotlib import pyplot as plt

source = "latency"
filename_pattern = re.compile(".*(sub-(\\d+)_broker-([rd])).*")
output_plot = "boxplot.png"
output_stat = "boxplot.txt"


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
    print("Analyzing...")
    df, cols = import_data()
    df.sort_index(axis=1)

    plt.figure()
    df.boxplot(column=cols)
    plt.savefig(output_plot, format="png")
    print(f"Generated plot: {output_plot}")

    mode_df = pd.DataFrame()
    for name in cols:
        mode_df[name] = df[name].mode()
    mode_df.index = ['mode']

    print(f"Statistics:  {output_stat}")
    f = open(output_stat, "w")
    f.write(df.describe().append(mode_df, sort=True).to_string())
    f.close()


if __name__ == "__main__":
    main()
