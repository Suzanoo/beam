import os
import numpy as np
import pandas as pd
from absl import app, flags
from absl.flags import FLAGS

"""
Deep Beam:
    -simple beam: h/ln > 4/5 
    -contineous: h/ln > 2/5

Critical section:
    -Distribution load: 0.15ln <= d
    -Point load: 0.50a <= d
"""


## FLAGS definition
# https://stackoverflow.com/questions/69471891/clarification-regarding-abseil-library-flags

flags.DEFINE_float("fc", 18, "240ksc, MPa")
flags.DEFINE_integer("fy", 295, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_integer("c", 3, "concrete covering, cm")

flags.DEFINE_integer("main", 12, "initial main bar definition, mm")
flags.DEFINE_integer("trav", 6, "initial traverse bar definition, mm")
flags.DEFINE_integer("b", 0, "beam width, cm")
flags.DEFINE_integer("h", 0, "beam heigth, cm")
flags.DEFINE_integer("l", 0, "beam length, m")
flags.DEFINE_float("Mu", 0, "Moment, kN-m")
flags.DEFINE_float("Vu", 0, "Shear, kN")

from beam_class import Beam
from shear import ShearCapacity, ShearReinforcement
from rebar import Rebar
from beam_analysis import Analysis

from utils import display_df
from plot_section import multi_sections, create_html

## Constance
Es = 2e5  # MPa
𝜙b = 0.9
𝜙v = 0.85

rebar = Rebar()

CURRENT = os.getcwd()


def max_shear_capacity(ln, d):

    if (ln / d) < 2:
        return 𝜙v * (2 / 3) * np.sqrt(FLAGS.fc) * FLAGS.b * d * 1e-1  # kN
    elif 2 <= (ln / d) <= 5:
        return (
            𝜙v * (1 / 18) * (10 + ln / d) * np.sqrt(FLAGS.fc) * FLAGS.b * d * 1e-1
        )  # kN
    else:
        return None


def main(_argv):
    print("=============== DEEPL BEAM DESIGN : USD METHOD ===============")

    print("PROPERTIES")
    print(
        f"f'c = {FLAGS.fc} Mpa, fy = {FLAGS.fy} Mpa, fv = {FLAGS.fv} MPa, Es = {Es:.0f} MPa"
    )
    print(f"𝜙b = {𝜙b}, 𝜙v = {𝜙v}")

    print(f"\nGEOMETRY")
    print(f"b = {FLAGS.b} cm, h = {FLAGS.h} cm,l = {FLAGS.l} m")

    # Deep beam or NOT!
    # if (FLAGS.h / FLAGS.l * 1e2) > (2 / 5):
    #     print(
    #         f"\n[WARNING!] h/ln > 2/5, Not a deep beaml, please use beam_design.py instead or revise your section! "
    #     )
    #     return

    # Instanciate
    beam = Beam(fc=FLAGS.fc, fy=FLAGS.fy, fv=FLAGS.fv, c=FLAGS.c)

    beam.section_properties(FLAGS.main, FLAGS.trav, FLAGS.b, FLAGS.h)
    d, d1 = beam.eff_depth()  # cm
    beam.capacity()

    # Max.shear capacity check for section
    # if (FLAGS.l * 100 / d) > 5:
    #     print(
    #         f"\n[WARNING!] ln / d > 5, max.shear capacity meet critical, please revise your section!"
    #     )
    #     return

    # --------------------------------
    ## Aanalysis
    # --------------------------------
    ask = input(
        f"\nDo you want execute beam analysis to display SFD and BMD! Y|N :"
    ).upper()
    if ask == "Y":
        analysis = Analysis()
        I = (1 / 12) * FLAGS.b * (FLAGS.h**3)  # cm4

        # spans, supports, loads, R0 = analysis()
        sfd_bmd_fig = analysis.analysis(FLAGS.E * 1e-3, I * 1e-8)
    else:
        sfd_bmd_fig = None

    # --------------------------------
    ## Design reinforcement
    # --------------------------------
    # Storage for plotting
    N = []
    main_reinf = []
    traverse_reinf = []
    middle_reinf = []
    no_of_middle_rebars = []
    spacing = []
    n = 1
    legend = []

    ln = FLAGS.l * 100 - (2 * d)  # cm

    # Display rebar df
    table = os.path.join(CURRENT, "data/Deform_Bar.csv")
    df = pd.read_csv(table)
    display_df(df)

    while True:
        print(f"\n--------------- SECTION-{n} -----------------")
        Mu = float(input("Define Mu in kN-m : "))
        Vu = float(input("Define Vu in kN : "))

        # --------------------------------
        ## Main reinforcement
        # --------------------------------
        # Check classification
        beam.classification(Mu)

        # Main bar required
        beam.mainbar_req(Mu)

        # Design main reinf
        no, main_dia, As_main = beam.main_design()

        # Design traverse
        # traverse_dia, Av, s = beam.traverse_design(d, Vu)

        # --------------------------------
        ## Traverse and Horizontal reinforcement
        # --------------------------------
        # Traverse
        shearCapacity = ShearCapacity(FLAGS.fc, FLAGS.fv)
        𝜙Vc = shearCapacity.flexural_shear(FLAGS.b, d)

        # Horizontal
        shearReinf = ShearReinforcement(FLAGS.fc, FLAGS.fv, FLAGS.fy)

        traverse_dia, s, horizontal_dia, s2, n2, 𝜙Vs, label = shearReinf.deepBeam(
            FLAGS.b, d, ln
        )

        # PLot tile
        if label == "Single stirrup":
            text = f"Main: {no} - ø{main_dia}mm, \nTraverse: ø{traverse_dia}mm @ {s} cm, \nLong.reinf.: ø{horizontal_dia}mm @ {s2} cm"
        else:
            text = f"Main: {no} - ø{main_dia}mm, \nTraverse: 2-ø{traverse_dia}mm @ {s} cm, \nLong.reinf.: ø{horizontal_dia}mm @ {s2} cm"

        # Check condition of 𝜙Vn
        𝜙Vn = 𝜙Vc + 𝜙Vs
        𝜙Vnmax = max_shear_capacity(ln, d)

        if 𝜙Vn <= 𝜙Vnmax:
            print(
                f"𝜙Vc = {𝜙Vc:.2f} kN, 𝜙Vs = {𝜙Vs:.2f} kN, 𝜙Vn = {𝜙Vn:.2f} kN, 𝜙Vnmax = {𝜙Vnmax:.2f} kN,"
            )
            print(f"SECTION OK")
        else:
            print(f"𝜙Vn > 𝜙Vnmax, SECTION IS NOT OK, Try again!!")

        # Collect for plotting
        N.append(no)
        main_reinf.append(main_dia)
        traverse_reinf.append(traverse_dia)
        middle_reinf.append(horizontal_dia)
        spacing.append(s)
        no_of_middle_rebars.append(n2)
        legend.append(text)

        print(f"\n[REINF.] : ")
        print(f"Main reinforcement : {np.array(main_reinf)}")
        print(f"No.of Main reinforcement : {np.array(N)}")
        print(f"Traverse reinforcement : {np.array(traverse_reinf)}")
        print(f"Traverse spacing : {np.array(s)}")
        print(f"Horizontal reinforcement : {np.array(middle_reinf)}")

        ask = input("Design another section! Y|N :").upper()
        if ask == "Y":
            n += n
        else:
            break

    # Rebars in each layer
    print(f"\n--------------- REBARS LAYING IN SECTION -----------------")
    bottom_layer, top_layer = rebar.rebar_laying(n, legend)

    # Create section fig.
    sections_fig = multi_sections(
        n,
        FLAGS.b,
        FLAGS.h,
        FLAGS.c,
        (np.array(main_reinf) / 10).tolist(),  # Convert mm to cm and re-convert to list
        (
            np.array(traverse_reinf) / 10
        ).tolist(),  # Convert mm to cm and re-convert to list
        (
            np.array(middle_reinf) / 10
        ).tolist(),  # Convert mm to cm and re-convert to list
        bottom_layer,
        top_layer,
        no_of_middle_rebars,
        legend,
    )

    create_html(sfd_bmd_fig, sections_fig)


if __name__ == "__main__":
    app.run(main)

"""
    % cd <path to project directory>
    % conda activate <your conda env name>
    % python app/deep_beam.py --b=60 --h=100 --l=5
    % python app/deep_beam.py --fc=24 --fy=395 --b=35 --h=100 --l=4

"""
