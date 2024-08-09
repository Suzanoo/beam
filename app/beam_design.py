import os
import pandas as pd

from absl import app, flags
from absl.flags import FLAGS

from beam_class import Beam
from torsion import Torsion
from rebar import Rebar
from beam_analysis import Analysis

from utils import display_df, convert_input_to_list
from plot_section import create_html

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
flags.DEFINE_float("Mu", 0, "Moment, kN-m")
flags.DEFINE_float("Vu", 0, "Shear, kN")
flags.DEFINE_float("Tu", 0, "Torsion, kN-m")

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
    beam = Beam(fc=FLAGS.fc, fy=FLAGS.fy, fv=FLAGS.fv, c=FLAGS.c)
    beam.section_properties(FLAGS.main, FLAGS.trav, FLAGS.b, FLAGS.h)
    d, d1 = beam.eff_depth()
    𝜙Mn1 = beam.capacity(d)

    # --------------------------------
    ## Aanalysis
    # --------------------------------
    ask = input(f"\nExecute beam analysis to display SFD and BMD! Y|N :").upper()
    if ask == "Y":
        analysis = Analysis()
        I = (1 / 12) * FLAGS.b * (FLAGS.h**3)  # cm4

        # spans, supports, loads, R0 = analysis()
        fig = analysis.analysis(FLAGS.E * 1e-3, I * 1e-8)
    else:
        fig = None

    # --------------------------------
    ## Design
    # --------------------------------
    N = []
    main_reinf = []
    traverse_reinf = []
    spacing = []
    n = 1

    # Display rebar df
    table = os.path.join(CURRENT, "data/Deform_Bar.csv")
    df = pd.read_csv(table)
    display_df(df)

    # Design reinforce
    while True:
        print(f"\n--------------- SECTION-{n} -----------------")
        Mu = float(input("Define Mu in kN-m : "))
        Vu = float(input("Define Vu in kN : "))

        # Check classification
        classify = beam.classification(Mu, 𝜙Mn1)

        # Main bar required
        data = beam.mainbar_req(d, d1, 𝜙Mn1, Mu, classify)

        # Design main reinf
        no, main_dia, As_main = beam.main_design(data)

        # Design traverse
        traverse_dia, Av, s = beam.traverse_design(d, Vu)

        # Collect for plotting
        N.append(no)
        main_reinf.append(main_dia)
        traverse_reinf.append(traverse_dia)
        spacing.append(s)

        ask = input("Design another section! Y|N :").upper()
        if ask == "Y":
            n += n
        else:
            break

    # Rebars in each layer
    bottom_layer, top_layer, middle_layer = rebar.rebar_laying(n)

    create_html(
        fig,
        n,
        FLAGS.b,
        FLAGS.h,
        FLAGS.c,
        traverse_reinf,
        main_reinf,
        bottom_layer,
        top_layer,
        middle_layer,
    )

    # Torsion reinf
    # if FLAGS.Tu != 0:
    #     print("")
    #     logging.info(f"[INFO] : TORSION")

    #     Acp = FLAGS.b * FLAGS.h
    #     Pcp = 2 * (FLAGS.b + FLAGS.h)

    #     torsion = Torsion(
    #         FLAGS.fc, FLAGS.fv, FLAGS.fy, FLAGS.fv, FLAGS.fy, FLAGS.Vu, FLAGS.Tu
    #     )

    #     torsion.section_properties(FLAGS.b, FLAGS.h, FLAGS.c, d, dia_trav)

    #     torsion.condition(Acp, Pcp)
    #     torsion.section(FLAGS.b, d)

    #     # New traverse
    #     torsion.traverse(FLAGS.b)

    #     # Long-reinforcment
    #     Al = torsion.longitudinal_reinf(FLAGS.b, Acp)

    #     print(f"\nFor Each Side : ")
    #     rebar.rebar_design(Al / 4)

    #     # Merge flexural and torsion reinf.
    #     print(f"\nModify Main Reinforcement : ")
    #     As = As_main + Al / 4
    #     dia_main, As_main = rebar.rebar_design(As)

    # TODO Development Length
    # print(f"\nDevelopment Length : ")
    # devLength = DevLength(FLAGS.fc, FLAGS.fy)

    # N = int(input(f"Provide number of main reinforce on bottom layer : "))
    # devLength.tensile(FLAGS.b, FLAGS.c, dia_main, N)


if __name__ == "__main__":
    app.run(main)

"""
How to used?
-Please see FLAGS definition for alternative
-Make sure you are in the project directory 
-run script
    % cd <path to project directory>
    % conda activate <your conda env name>
    % python app/beam_design.py --b=3000 --h=24
    % python app/beam_design.py --b=40 --h=60

    
"""
