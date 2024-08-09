import numpy as np
from tabulate import tabulate


def to_numpy(s):
    return np.fromstring(s, sep=" ")


def get_valid_integer(prompt):
    while True:
        user_input = input(prompt)
        if user_input.isdigit():
            return int(user_input)
        else:
            print("Invalid input. Please enter a valid number.")


def get_valid_number(prompt):
    while True:
        user_input = input(prompt)
        try:
            # Try to convert the input to a float
            value = float(user_input)
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_valid_list_input(prompt):
    while True:
        user_input = input(prompt)
        try:
            array = to_numpy(user_input)
            if len(array) == 0:
                raise ValueError("No valid numbers found.")
            return array  # Numpy arrays
        except ValueError as e:
            print(
                f"Invalid input: {e}. Please enter a space-separated list of numbers."
            )


def convert_input_to_list(input_string):
    return list(map(int, input_string.split()))


# Assembly X-coordinate
def xi_coordinate(spans):
    numS = 1000  # Number of points per span
    Xt = [np.linspace(0, span, numS) for span in spans]
    return numS, Xt


# X-coordinate
def X_coordinate(spans, stretch, Xt):
    X = []
    temp = 0
    for i in range(len(spans)):
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
