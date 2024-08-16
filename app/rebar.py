from utils import convert_input_to_list


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
            print(f"As required = {As:.2f} cm2, please select")
            dia, A = self.rebar_selected()
            N = int(input("Quantities N = ? : "))

            if N * A > As:
                print(f"Reinforcment : {N} - ø{dia} mm = {N * A:.2f} cm2")
                return N, dia, N * A
            else:
                print(
                    f"As provide : {N} - ø{dia} mm = {N * A:.2f} cm2 < {As:.2f} cm2, Try again!"
                )

    def rebar_laying(self, n, legend):
        # Rebars in each layer
        bottom_layer = []
        top_layer = []
        # no_of_middle_rebars = []

        for i in range(n):
            print(f"\nSection-{i+1} : {legend[i]}")
            bott = convert_input_to_list(
                input(f"Lay rebars in bottom layer, ex. 3 2 : ")
            )
            top = convert_input_to_list(input(f"Lay rebars in top layer, ex. 3 2 : "))
            # middle = int(
            #     input(
            #         f"Section-{i+1}, How many middle rebar? Even numbers only, ex. 4 : "
            #     )
            # )
            # TODO check middle is even number
            bottom_layer.append(bott)
            top_layer.append(top)
            # no_of_middle_rebars.append(middle)

        return bottom_layer, top_layer
