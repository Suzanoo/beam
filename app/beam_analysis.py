#!/usr/bin/env python3
import numpy as np


from absl import app, flags
from absl.flags import FLAGS

from diagram import DistributedLoad, MomentConcentrated, PointLoad
import diagram as diagram

from utils import get_valid_integer, get_valid_list_input

flags.DEFINE_float("E", 200, "GPa")
# flags.DEFINE_float("b", 0, "beam width, cm")
# flags.DEFINE_float("h", 0, "beam depth, cm")


class Analysis:

    def __init__(self):
        print("Hello, world!")
        pass

    def __str__(self) -> str:
        pass

    def spans_length(self):
        N = get_valid_integer("How many span? : ")

        while True:
            while True:
                try:
                    spans = get_valid_list_input(
                        "Define array of spans in meters, ex 4 4 5: "
                    )

                    if spans.size == N:
                        print(f"spans = {spans}")
                        break
                    else:
                        print(
                            f"You need to define exactly {N} spans. You provided {spans.size}. Try again."
                        )
                except ValueError as e:
                    print(f"Input error: {e}. Please try again.")
                except Exception as e:
                    print(f"Unexpected error: {e}. Please try again.")

            ask = input("Try again! Y|N : ").upper()
            if ask == "Y":
                pass
            else:
                break

        self.spans = spans.tolist()

        # --------------------------------------------------------------------

    def supports_type(self):
        ## Support type
        supports = []
        print(
            f"\nDefine support type for each node. You have {len(self.spans)+1} nodes"
        )
        while True:
            for i in range(1, len(self.spans) + 2):
                while True:

                    x = get_valid_integer(
                        f"Define support type for node {i} from fixd=0, vert-scroll=1, pin=2, free=3 : "
                    )
                    if x in [0, 1, 2, 3]:
                        supports.append(x)
                        print(f"support type = {supports}")
                        break
                    else:
                        print("Choose from [0, 1, 2, 3].Try again")

            ask = input(f"Try again!  Y|N : ").upper()
            if ask == "Y":
                supports = []
            else:
                break

        self.supports = supports

        # --------------------------------------------------------------------

    def ext_loads(self):
        ## Nodal external loads
        """
        Define external loads for each node.
        For each node first define is Fy(kN), next is M(kN-m)
        Finaly we have [R0] = ['F1y', 'M1', 'F2y', 'M2', 'F3y', 'M3',...]
        """
        R0 = []
        print(
            f"\nDefine external loads(R0) at each node. You have {len(self.supports)} nodes"
        )
        while True:
            for i in range(1, len(self.supports) + 1):
                while True:
                    try:
                        f = float(input(f"Define Fy(kN) for node {i} Up-, Down+ : "))
                        m = float(
                            input(
                                f"Define moment(kN-m) for node {i} counterclockwise + : "
                            )
                        )
                        R0.append(f)
                        R0.append(m)
                        print(f"R0 = {R0}")
                        break
                    except Exception as e:
                        print("Badly input.Try again")

            ask = input(f"Try again!  Y|N : ").upper()
            if ask == "Y":
                R0 = []
            else:
                break
        self.R0 = R0

        # --------------------------------------------------------------------

    def loads_type(self):
        # Define loads in each stretch : unit in --> Newton, N
        """
        q = DistributedLoad (value, start, length), distance between the left end of the span and the start of the load
        P = PointLoad(value, position), Load position with respect to the left end of the section
        M = MomentConcentrated (value, position),  position of the moment with respect to the left end of the section'
        """
        print(f"\nDefine loads in each stretch : unit in --> Newton, Newton-meters")
        print(f"You have {len(self.spans)} stretch")

        loads = [[] for i in range(0, len(self.spans))]  # [[], [], [],...]
        for i in range(0, len(loads)):
            print(f"Define load for stretch {i+1} :")
            while True:
                try:
                    type = input(
                        "Choose load type(P, q , M) or other keyboard type if none : "
                    ).lower()
                    if type in ("p", "q", "m"):
                        if type == "p":
                            value = (
                                float(input("Enter point load P(kN) , Down+ Up- : "))
                                * 1e3  # convert kN to N
                            )
                            x = float(
                                input(
                                    "Enter position x(m) with respect to the left end of the section : "
                                )
                            )
                            f = PointLoad(value, x)
                            loads[i].append(f)

                        elif type == "q":
                            value = (
                                float(
                                    input(
                                        "Enter line load value q(kN/m) , Down+ Up- : "
                                    )
                                )
                                * 1e3
                            )
                            start = float(
                                input(
                                    "Enter start point x(m) distance between the left end of the span and the start of the load : "
                                )
                            )
                            length = float(input("Enter length of line load l(m) : "))
                            f = DistributedLoad(value, start, length)
                            loads[i].append(f)
                        else:
                            value = float(input("Enter moment m(N-m) : ")) * 1e3
                            x = float(
                                input(
                                    "Enter position x(m) relative to the left node of the stretch, counterclockwise + : "
                                )
                            )
                            f = MomentConcentrated(value, x)
                            loads[i].append(f)
                    else:
                        print(f"None for stretch {i+1}")
                        break

                    ask = input(f"Finish for stretch {i+1} Y|N : ").upper()
                    if ask == "Y":
                        break
                except:
                    print("Badly input.Try again")
            print("#---------------------------------------------")
        self.loads = loads

        # return spans, supports, loads, R0

    def analysis(self, E=0, I=0):
        print("=============== BEAM ANALYSIS : METRIX STIFFNESS METHOD ===============")
        print("Code adopt from Prof. Fredy Gabriel Ramírez Villanueva repository")
        print("https://github.com/SirPrime/MatrixAnalysis-Beams.git")
        print("")
        print("https://www.youtube.com/watch?v=hCmXwMQWafk&list=LL&index=6&t=3642s")
        print(
            "https://www.erbakan.edu.tr/storage/files/department/insaatmuhendisligi/editor/DersSayfalari/YapSt2/06_Matrix_Beam.pdf"
        )

        if I == 0:
            I = (
                float(input(f"Defint moment of inertia(I) in cm4 : ")) * 1e-8
            )  # convert to m4

        if E == 0:
            E = FLAGS.E

        self.spans_length()
        self.supports_type()
        self.ext_loads()
        self.loads_type()

        fig = diagram.main(E, I, self.spans, self.supports, self.loads, self.R0)
        return fig


def main(_argv):
    analysis = Analysis()
    analysis.analysis()


if __name__ == "__main__":
    app.run(main)


# --------------------------------------------------------------------
"""
 % python app/beam_analysis.py 
"""
