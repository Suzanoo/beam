import numpy as np
from tabulate import tabulate


def convert_input_to_list(input_string):
    return list(map(int, input_string.split()))


# Assembly X-coordinate
def xi_coordinate(spans, stretch):
    numS = 1000
    Xt = []
    for i in range(spans):
        Xt.append(np.linspace(0, stretch[i].L, numS))  # 1000 points in each stretch
    return numS, Xt


# X-coordinate
def X_coordinate(spans, stretch, Xt):
    X = []
    temp = 0
    for i in range(spans):
        if i > 0:
            temp += stretch[i - 1].L
        Xprov = Xt[i] + temp
        Xlist = Xprov.tolist()
        X += Xlist
    return X


# Display rebar table
def display_df(df):
    print(f"\nDATABASE")
    print(
        tabulate(
            df,
            headers=df.columns,
            floatfmt=".2f",
            showindex=False,
            tablefmt="psql",
        )
    )
