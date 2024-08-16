import os
import numpy as np
import pandas as pd

from absl import app, flags
from absl.flags import FLAGS

from beam_class import Beam
from torsion import Torsion
from rebar import Rebar
from beam_analysis import Analysis

from utils import display_df
from plot_section import multi_sections, create_html

# from rc.devLength import DevLength

## FLAGS definition
# https://stackoverflow.com/questions/69471891/clarification-regarding-abseil-library-flags

flags.DEFINE_float("fc", 24, "240ksc, MPa")
flags.DEFINE_integer("fy", 390, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_float("c", 3, "concrete covering, cm")

flags.DEFINE_integer("main", 12, "initial main bar definition, mm")
flags.DEFINE_integer("trav", 6, "initial traverse bar definition, mm")
flags.DEFINE_float("b", 0, "beam width, cm")
flags.DEFINE_float("h", 0, "beam heigth, cm")

Es = 2e5  # MPa
𝜙b = 0.9
𝜙v = 0.85

rebar = Rebar()

CURRENT = os.getcwd()


# ----------------------------------
def main(_argv):
    print("=============== TYPICAL BEAM DESIGN : USD METHOD ===============")

    print("PROPERTIES")
    print(
        f"f'c = {FLAGS.fc} Mpa, fy = {FLAGS.fy} Mpa, fv = {FLAGS.fv} MPa, Es = {Es:.0f} MPa"
    )
    print(f"𝜙b = {𝜙b}, 𝜙v = {𝜙v}")

    print(f"\nGEOMETRY")
    print(f"b = {FLAGS.b} cm, h = {FLAGS.h} cm,")

    # instanciate
    # Instanciate
    beam = Beam(fc=FLAGS.fc, fy=FLAGS.fy, fv=FLAGS.fv, c=FLAGS.c)

    beam.section_properties(FLAGS.main, FLAGS.trav, FLAGS.b, FLAGS.h)
    d, d1 = beam.eff_depth()
    beam.capacity()

    # --------------------------------
    ## Aanalysis
    # --------------------------------
    ask = input(
        f"\nDo you want to xecute beam analysis to display SFD and BMD! Y|N :"
    ).upper()
    if ask == "Y":
        analysis = Analysis()
        I = (1 / 12) * FLAGS.b * (FLAGS.h**3)  # cm4

        # spans, supports, loads, R0 = analysis()
        sfd_bmd_fig = analysis.analysis(FLAGS.E * 1e-3, I * 1e-8)
    else:
        sfd_bmd_fig = None

    # --------------------------------
    ## Design
    # --------------------------------
    N = []
    main_reinf = []
    traverse_reinf = []
    middle_reinf = []
    no_of_middle_rebars = []
    spacing = []
    n = 1

    # Display rebar df
    table = os.path.join(CURRENT, "data/Deform_Bar.csv")
    df = pd.read_csv(table)
    display_df(df)

    # Design reinforce
    while True:
        print(f"\n--------------- SECTION-{n} -----------------")
        Mu = float(input("Define Mmoment, Mu in kN-m : "))
        Vu = float(input("Define Shear, Vu in kN : "))
        Tu = float(input("Define Torsion, Tu in kN-m : "))

        # Check classification
        beam.classification(Mu)

        # Main bar required
        beam.mainbar_req(Mu)

        # Design main reinf
        no, main_dia, As_main = beam.main_design()

        # Design traverse
        traverse_dia, Av, s = beam.traverse_design(Vu)

        # Design longitudinal reinforcement
        if Tu != 0:

            Acp = FLAGS.b * FLAGS.h
            Pcp = 2 * (FLAGS.b + FLAGS.h)

            torsion = Torsion(FLAGS.fc, FLAGS.fv, FLAGS.fy, FLAGS.fv, FLAGS.fy, Vu, Tu)

            (
                no_of_main,
                new_main_dia,
                new_traverse,
                new_spacing,
                no_of_long_rebar,
                long_reinf_dia,
            ) = torsion.design(
                FLAGS.b, FLAGS.h, FLAGS.c, d, As_main, traverse_dia, Vu, Tu
            )

            # Collect for plotting if Torsion
            N.append(no_of_main)
            main_reinf.append(new_main_dia / 10)  # Conver mm to cm
            traverse_reinf.append(new_traverse / 10)  # Conver mm to cm
            spacing.append(new_spacing)
            no_of_middle_rebars.append(no_of_long_rebar)
            middle_reinf.append(long_reinf_dia / 10)  # Conver mm to cm

        # Collect for plotting if no Torsion
        N.append(no)
        main_reinf.append(main_dia / 10)  # Conver mm to cm
        traverse_reinf.append(traverse_dia / 10)  # Conver mm to cm
        spacing.append(s)
        middle_reinf.append(0)
        no_of_middle_rebars.append(0)

        #
        print(f"\n[REINF.] : ")
        print(f"Main reinforcement : {np.array(main_reinf)}")
        print(f"No.of Main reinforcement : {np.array(N)}")
        print(f"Traverse reinforcement : {np.array(traverse_reinf)}")
        print(f"Traverse spacing : {np.array(spacing)}")
        print(f"Horizontal reinforcement : {np.array(middle_reinf)}")
        print(f"No. of Horizontal reinforcement : {np.array(no_of_middle_rebars)}")

        ask = input(f"\nDesign another section! Y|N :").upper()
        if ask == "Y":
            n += n
        else:
            break

    # Rebars in each layer
    print(f"\n--------------- REBARS LAYING IN SECTION -----------------")
    bottom_layer, top_layer = rebar.rebar_laying(n)

    # Create section fig.
    sections_fig = multi_sections(
        n,
        FLAGS.b,
        FLAGS.h,
        FLAGS.c,
        main_reinf,
        traverse_reinf,
        middle_reinf,
        bottom_layer,
        top_layer,
        no_of_middle_rebars,
    )

    create_html(sfd_bmd_fig, sections_fig)

    # TODO Development Length
    # print(f"\nDevelopment Length : ")
    # devLength = DevLength(FLAGS.fc, FLAGS.fy)

    # N = int(input(f"Provide number of main reinforce on bottom layer : "))
    # devLength.tensile(FLAGS.b, FLAGS.c, dia_main, N)


if __name__ == "__main__":
    app.run(main)

"""
-run script
    % cd <path to project directory>
    % conda activate <your conda env name>
    % python app/beam_design.py --b=3000 --h=24
    % python app/beam_design.py --b=40 --h=60

    
"""
