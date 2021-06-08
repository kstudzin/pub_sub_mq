import os
import pathlib

import pandas as pd

source = "latency"


def import_data():
    df = pd.DataFrame()
    for file in os.listdir(source):
        name = pathlib.Path(file).stem
        df_curr = pd.read_csv(os.path.join(source, file), header=None, usecols=[0], names=[name])
        df[name] = df_curr[name]
    return df


def main():
    df = import_data()
    print(df.head(10))


if __name__ == "__main__":
    main()