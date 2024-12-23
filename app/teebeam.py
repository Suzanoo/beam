import os
import pandas as pd
from absl import app, flags
from absl.flags import FLAGS

from beam import (
    MaterialProperties,
    SectionGeometry,
    Reinforcement,
    Loads,
    ReinforcementCalculator,
)
from section_generator import SectionGenerator
from rebar import Rebar
from shear import ShearReinforcement
from torsion import Torsion
from torsion import Torsion

from utils import display_df, get_valid_number

# from tools.devLength import DevLength

## FLAGS definition
# https://stackoverflow.com/questions/69471891/clarification-regarding-abseil-library-flags

flags.DEFINE_float("fc", 18, "240ksc, MPa")
flags.DEFINE_integer("fy", 295, "SD40 main bar, MPa")
flags.DEFINE_integer("fv", 235, "SR24 traverse, MPa")
flags.DEFINE_integer("c", 3, "concrete covering, cm")

flags.DEFINE_integer("main", 12, "initial main bar definition, mm")
flags.DEFINE_integer("trav", 9, "initial traverse bar definition, mm")

flags.DEFINE_integer("b", 0, "beam width, cm")
flags.DEFINE_integer("bw", 0, "web width, cm")

flags.DEFINE_integer("h", 0, "beam heigth, cm")
flags.DEFINE_integer("hf", 0, "flange heigth(slab), cm")

flags.DEFINE_integer("l", 0, "beam length, m")

flags.DEFINE_float("Mu", 0, "Moment, kN-m")
flags.DEFINE_float("Vu", 0, "Shear, kN")
flags.DEFINE_float("Tu", 0, "Torsion, kN-m")

Es = 2e5  # MPa
𝜙b = 0.9
𝜙v = 0.85

CURRENT = os.getcwd()


# ----------------------------------
## Tee beam
# ----------------------------------
def neutal_axis(β1, p, d):
    w = p * FLAGS.fy / FLAGS.fc
    a = w * d / 0.85  # cm
    c = a / β1  # cm
    print(f"\nNuetral axis = {c:.2f} cm")
    return c


def tee_capacity(d, As):
    a = (As * FLAGS.fy - 0.85 * FLAGS.fc * FLAGS.hf * (FLAGS.b - FLAGS.bw)) / (
        0.85 * FLAGS.fc * FLAGS.bw
    )  # cm

    𝜙Mw = 0.85 * FLAGS.fc * a * FLAGS.bw * (d - a / 2) * 1e-3  # kN-m
    𝜙Mf = (
        0.85 * FLAGS.fc * (FLAGS.b - FLAGS.bw) * FLAGS.hf * (d - FLAGS.h / 2) * 1e-3
    )  # kN-m

    𝜙Mn1 = 𝜙Mw + 𝜙Mf

    return 𝜙Mn1


def main(_argv):
    print(
        "============================== TEE BEAM DESIGN : USD METHOD ============================== "
    )

    # =================================================================
    ## Initialized
    # =================================================================
    materials = MaterialProperties(fc=25, fv=235, fy=390, Es=200000)
    print(materials)

    geometry = SectionGeometry()
    geometry.tee_beam(FLAGS.b, FLAGS.bw, FLAGS.h, FLAGS.hf, FLAGS.l)

    reinforcement = Reinforcement(main_dia=16, traverse_dia=9)

    section = SectionGenerator(materials, geometry, reinforcement)
    section.section_properties(covering=2.5)

    rebar_object = Rebar()

    shear_object = ShearReinforcement(materials)

    # =================================================================
    ## Check tee beam conditions
    # =================================================================
    # Check nuetral axis
    c = neutal_axis(materials.β1, section.p, section.d)

    # Calculate 𝜙Mn
    if c < FLAGS.hf:
        print("Rectangular Beam")

    else:
        As = section.p * geometry.b * section.d
        𝜙Mn1 = tee_capacity(section.d, As)
        print(f"\nTee Beam")
        print(f"New section capacity : \n𝜙Mn = {𝜙Mn1:.2f} kN-m")

        # Override 𝜙Mn1
        section.𝜙Mn1 = 𝜙Mn1

    # =================================================================
    ## Design
    # =================================================================
    # Display rebar df
    file_name = os.path.join(CURRENT, "data/Deform_Bar.csv")
    df = pd.read_csv(file_name)
    display_df(df)
    # Loads
    Mu = get_valid_number("Define Mu in kN-m : ")
    Vu = get_valid_number("Define Vu in kN : ")
    Tu = get_valid_number("Define Tu in kN : ")
    loads = Loads(Mu=Mu, Vu=Vu, Tu=Tu)

    # Calculate reinforcements required
    calculator = ReinforcementCalculator(section, loads)

    print(f"\n[INFO] Main Reinforcement")
    calculator.section_type()
    N, main, As = calculator.main_reinf(rebar_object)

    print(f"\n[INFO] Traverse Reinforcement")
    while True:
        traverse, Av, spacing = calculator.traverse_reinf(shear_object, rebar_object)
        ask = input("Try again! : Y|N : ").upper()
        if ask != "Y":
            break

    # Design longitudinal reinforcement
    if Tu != 0:
        torsion = Torsion(materials, loads)
        context = torsion.design(
            geometry.b,
            geometry.h,
            section.d,
            As,
            traverse,
            c=2.5,
        )


if __name__ == "__main__":
    app.run(main)

"""
-run script
    % cd <path to project directory>
    % conda activate <your conda env name>
    % python app/teebeam.py --bw=30 --b=100 --hf=10 --h=40 --l=4 
    % python app/teebeam.py --fc=24 --fy=395 --bw=30 --b=100 --hf=10 --h=40 --l=5 
    
"""
