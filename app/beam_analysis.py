#!/usr/bin/env python3
import numpy as np


from absl import app, flags
from absl.flags import FLAGS

from diagram import DistributedLoad, MomentConcentrated, PointLoad
import diagram as diagram

flags.DEFINE_float("E", 200, "GPa")


def analysis():
    print("BEAM ANALYSIS : METRIX STIFFNESS METHOD")
    print("Code adopt from Prof. Fredy Gabriel Ramírez Villanueva repository")
    print("https://github.com/SirPrime/MatrixAnalysis-Beams.git")
    print("")
    print("Tutorial: YouTube Channel 'วิเคราะห์โครงสร้าง กับ อ.กิจ'")
    print("https://www.youtube.com/watch?v=hCmXwMQWafk&list=LL&index=6&t=3642s")
    print(
        "https://www.erbakan.edu.tr/storage/files/department/insaatmuhendisligi/editor/DersSayfalari/YapSt2/06_Matrix_Beam.pdf"
    )
    print(
        "========================================================================================="
    )

    ## Span of each stretch
    spans = []
    i = 1
    print("First : Define span of each stretch.")
    while True:
        try:
            s = float(input(f"Enter length for stretch {i} in meters : "))
            if s > 0:
                spans.append(s)
                print(f"span = {spans}")
                ask = input("Finish? Y|N : ").upper()
                if ask == "Y":
                    break
                else:
                    i += 1
            else:
                print("Badly input.Try again")
        except Exception as e:
            print("Badly input.Try again")

    # --------------------------------------------------------------------
    ## Support type
    supports = []
    print(f"\nDefine support type for each node. You have {len(spans)+1} nodes")
    while True:
        for i in range(1, len(spans) + 2):
            while True:
                try:
                    x = int(
                        input(
                            f"Define support type for node {i} --> fixd=0, vert-scroll=1, pin=2, free=3 : "
                        )
                    )
                    if x in [0, 1, 2, 3]:
                        supports.append(x)
                        print(f"support type = {supports}")
                        break
                    else:
                        print("Badly input.Try again")
                except Exception as e:
                    print("Badly input.Try again")

        ask = input(f"Try again!  Y|N : ").upper()
        if ask == "N":
            break

    # --------------------------------------------------------------------
    ## Nodal external loads
    """
    Define external loads for each node.
    For each node first define is Fy(kN), next is M(kN-m)
    Finaly we have [R0] = ['F1y', 'M1', 'F2y', 'M2', 'F3y', 'M3',...]
    """
    R0 = []
    print(f"\nDefine external loads(R0) at each node. You have {len(supports)} nodes")
    while True:
        for i in range(1, len(supports) + 1):
            while True:
                try:
                    f = float(input(f"Define Fy(kN) for node {i} Up-, Down+ : "))
                    m = float(
                        input(f"Define moment(kN-m) for node {i} counterclockwise + : ")
                    )
                    R0.append(f)
                    R0.append(m)
                    print(f"R0 = {R0}")
                    break
                except Exception as e:
                    print("Badly input.Try again")

        ask = input(f"Try again!  Y|N : ").upper()
        if ask == "N":
            break

    # --------------------------------------------------------------------
    # Define loads in each stretch : unit in --> Newton, N
    """
    q = DistributedLoad (value, start, length), distance between the left end of the span and the start of the load
    P = PointLoad(value, position), Load position with respect to the left end of the section
    M = MomentConcentrated (value, position),  position of the moment with respect to the left end of the section'
    """
    print(f"\nDefine loads in each stretch : unit in --> Newton, Newton-meters")
    print(f"You have {len(spans)} stretch")

    loads = [[] for i in range(0, len(spans))]  # [[], [], [],...]
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
                            float(input("Enter line load value q(kN/m) , Down+ Up- : "))
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

    return spans, supports, loads, R0


##Call
def main(_argv):
    I = float(input("Defint moment of inertia(I) in cm4 : ")) * 1e-8  # convert to m4

    spans, s, loads, R0 = analysis()

    diagram.main(FLAGS.E, I, spans, s, loads, R0)


if __name__ == "__main__":
    app.run(main)


# --------------------------------------------------------------------
"""
How to used?
-Please see FLAGS definition for unit informations
-Make sure you are in the project directory run python in terminal(Mac) or command line(Windows)

-Run app with flag I (moment of inertia)   
    % python app/beam_analysis.py 

"""
