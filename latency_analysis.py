import os
import pathlib

import pandas as pd
from matplotlib import pyplot as plt

source = "latency"


def import_data():
    df = pd.DataFrame()
    names = []
    for file in os.listdir(source):
        name = pathlib.Path(file).stem
        df_curr = pd.read_csv(os.path.join(source, file), header=None, usecols=[0], names=[name])
        df[name] = df_curr[name]
        names.append(name)
    return df, names


def main():
    df, cols = import_data()

    plt.figure()
    df.boxplot(column=cols)
    plt.savefig("test.png", format="png")


if __name__ == "__main__":
    main()