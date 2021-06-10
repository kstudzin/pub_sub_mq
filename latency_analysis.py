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
        if not match:
            continue
        num_subs = int(match.group(2))
        rows = num_subs * 1000
        name = "{0:03}_{1}".format(num_subs, match.group(3))
        df_curr = pd.read_csv(os.path.join(source, file), header=None, usecols=[0], names=[name], nrows=rows)
        df[name] = df_curr[name]
        names.append(name)

    names.sort()
    return df, names


def main():
    print("Analyzing...")
    df, cols = import_data()

    plt.figure()
    plt.title("PubSub Latency")
    boxplot = df.boxplot(column=cols, return_type='axes')
    boxplot.set_xlabel("Test Run (<number subscribers>_<routing|direct>)")
    boxplot.set_ylabel("Time (seconds)")
    plt.savefig(output_plot, format="png")
    print(f"Generated plot: {output_plot}")

    mode_df = pd.DataFrame()
    for name in cols:
        mode_df[name] = df[name].mode()

    df.sort_index(axis=1)
    print(f"Statistics:  {output_stat}")
    f = open(output_stat, "w")
    f.write("Statistics:\n\n")
    f.write(df.describe().sort_index(axis=1).to_string())
    f.write("\n\nMode:\n\n")
    f.write(mode_df.to_string())
    f.close()


if __name__ == "__main__":
    main()
