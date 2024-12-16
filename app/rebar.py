import pandas as pd

from utils import convert_input_to_list, get_valid_integer


class Rebar:
    def __init__(self) -> None:
        self.𝜙 = {
            "6": 6,
            "9": 9,
            "12": 12,
            "16": 16,
            "20": 20,
            "25": 25,
            "28": 28,
            "32": 32,
        }  # mm

        self.A = {
            "6": 0.2827,
            "9": 0.636,
            "12": 1.131,
            "16": 2.01,
            "20": 3.146,
            "25": 4.908,
            "28": 6.157,
            "32": 6.313,
        }  # cm2

    def rebar_selected(self):
        while True:
            dia = input(f"Select Diameter  = ? : ")
            if self.𝜙.get(dia) == None:
                print("Wrong diameter! select again")
            else:
                return int(dia), self.A[str(dia)]

    def rebar_design(self, As):
        while True:
            while True:
                print(f"As required = {As:.2f} cm2, please select")
                dia, A = self.rebar_selected()
                N = int(input("Quantities N = ? : "))

                if N * A > As:
                    print(f"Reinforcment : {N} - ø{dia} mm = {N * A:.2f} cm2")
                    break
                else:
                    print(
                        f"As provide : {N} - ø{dia} mm = {N * A:.2f} cm2 < {As:.2f} cm2, Try again!"
                    )
            ask = input("Try again! : Y|N : ").upper()
            if ask != "Y":
                return N, dia, N * A

    def rebar_laying(self):
        # Rebars in each layer
        bottom_layer = convert_input_to_list(
            input(f"Lay rebars in bottom layer, ex. 3 2 : ")
        )
        top_layer = convert_input_to_list(input(f"Lay rebars in top layer, ex. 3 2 : "))
        no_of_middle_rebars = int(
            get_valid_integer(
                "How many middle rebar, Even numbers only, ex. 2, 4, ... : "
            )
        )
        # TODO check middle is even number

        return bottom_layer, top_layer, no_of_middle_rebars

    def calculate_rebar_positions(self, c, b, N, main_dia, travesre_dia):
        if N == 1:
            return [c + (b - 2 * c) / 2]
        elif N == 2:
            return [
                c + travesre_dia + main_dia / 2,
                b - c - travesre_dia - main_dia / 2,
            ]
        else:
            positions = [
                c
                + main_dia / 2
                + travesre_dia
                + i * (b - 2 * c - main_dia - 2 * travesre_dia) / (N - 1)
                for i in range(N)
            ]
            return positions

    def get_rebar_coordinates(
        self, b, d, c, main_dia, travesre_dia, bottom_layers, top_layers, middle_rebars
    ):
        rebar_data = []

        # Calculate positions of top reinforcement layers
        layer_spacing = 2 * main_dia
        y_top_layers = [
            d - c - (i + 0.5) * layer_spacing for i in range(len(top_layers))
        ]

        for y, num_bars in zip(y_top_layers, top_layers):
            x_positions = self.calculate_rebar_positions(
                c, b, num_bars, main_dia, travesre_dia
            )
            for x in x_positions:
                z = d - y
                rebar_data.append({"x": x, "y": y, "z": z})

        # Calculate positions of bottom reinforcement layers

        y_bottom_layers = [
            c + (i + 0.5) * layer_spacing for i in range(len(bottom_layers))
        ]

        for y, num_bars in zip(y_bottom_layers, bottom_layers):
            x_positions = self.calculate_rebar_positions(
                c, b, num_bars, main_dia, travesre_dia
            )
            for x in x_positions:
                z = d - y
                rebar_data.append({"x": x, "y": y, "z": z})

        # Calculate positions of middle reinforcement layers
        if middle_rebars > 0:
            n = middle_rebars // 2
            d_middle = min(y_top_layers) - max(y_bottom_layers)
            s = d_middle / (n + 1)

            for i in range(1, n + 1):
                y_position = max(y_bottom_layers) + s * i
                z = d - y_position
                rebar_data.append(
                    {"x": c + travesre_dia + main_dia / 2, "y": y_position, "z": z}
                )
                rebar_data.append(
                    {"x": b - c - travesre_dia - main_dia / 2, "y": y_position, "z": z}
                )

        return pd.DataFrame(rebar_data)
