import os
import pandas as pd

from beam import (
    MaterialProperties,
    SectionGeometry,
    Reinforcement,
    Loads,
    ReinforcementCalculator,
)

from beam_analysis import BeamAnalysis

from section_generator import SectionGenerator

from rebar import Rebar
from shear import ShearCapacity, ShearReinforcement
from torsion import Torsion
from plot import Plot

from utils import display_df, get_valid_number

CURRENT = os.getcwd()

# =================================================================
## Initialized
# =================================================================
materials = MaterialProperties(fc=25, fv=235, fy=390, Es=200000)
print(materials)

geometry = SectionGeometry()
geometry.rectangle(b=30, h=60, l=5)
print(geometry)

reinforcement = Reinforcement(main_dia=16, traverse_dia=9)

section = SectionGenerator(materials, geometry, reinforcement)
section.section_properties(covering=2.5)

rebar_object = Rebar()

shear_object = ShearReinforcement(materials)

# Deep beam or NOT!
if (geometry.h / geometry.l * 1e2) < (2 / 5):
    print(f"\n[WARNING!] h/ln < 2/5 and it is not deep beam")

# =================================================================
## Beam Analysis
# =================================================================
if input(f"\nDo you want to execute 'beam analysis' : Y|N ").upper() == "Y":

    I = (1 / 12) * geometry.b * (geometry.h**3)  # cm4

    print(f"Self weigth : {geometry.b * geometry.h * 2.4*9.81 *1e-4:.2f} kN/m")

    analysis = BeamAnalysis(materials.Es * 1e-3, I * 1e-8)
    analysis.calculators_force()
    curve_fig = analysis.plot_diagram()
else:
    curve_fig = None

# =================================================================
## Design
# =================================================================
# Display rebar df
file_name = os.path.join(CURRENT, "data/Deform_Bar.csv")
df = pd.read_csv(file_name)
display_df(df)


# Design foe n section
n = 1
_main, _traverse, _long = [], [], []
while True:
    print(f"===================Section-{n}===================")

    # Loads
    Mu = get_valid_number("Define Mu in kN-m : ")
    Vu = get_valid_number("Define Vu in kN : ")
    Tu = get_valid_number("Define Tu in kN : ")
    loads = Loads(Mu=Mu, Vu=Vu, Tu=Tu)

    # Calculate reinforcements required
    calculator = ReinforcementCalculator(section, loads)

    print(f"\n[CALC.] Main Reinforcement")
    calculator.section_type()
    N, main, As = calculator.main_reinf(rebar_object)

    print(f"\n[CALC.] Traverse Reinforcement")
    shearCapacity = ShearCapacity(materials.fc, materials.fv)
    𝜙Vc = shearCapacity.flexural_shear(geometry.b, section.d)

    while True:
        traverse, spacing, long_reinf, s2, N_long, 𝜙Vs, label = shear_object.deepBeam(
            geometry.b, section.d, geometry.l * 100
        )
        if input("Try again! : Y|N : ").upper() != "Y":
            break

    # Check condition of 𝜙Vn
    # print(f"\n[CHECK] Shear Condition")s
    # 𝜙Vn = 𝜙Vc + 𝜙Vs
    # 𝜙Vnmax = shearCapacity.max_shear_capacity(geometry.b, geometry.l * 1e2, section.d)
    # if 𝜙Vnmax != None and 𝜙Vn <= 𝜙Vnmax:
    #     print(f"SECTION OK")
    # else:
    #     sys.exit("𝜙Vn > 𝜙Vnmax, SECTION IS NOT OK, Create new section and Try Again!")
    #     break

    # Design longitudinal reinforcement
    # if Tu != 0:
    #     torsion = Torsion(materials, loads)
    #     context = torsion.design(
    #         geometry.b,
    #         geometry.h,
    #         section.d,
    #         As,
    #         traverse,
    #         c=2.5,
    #     )
    #     # New value
    #     main = context["new_main"]
    #     N = context["new_N"]
    #     traverse = context["new_traverse"]
    #     spacing = context["new_spacing"]
    #     long_reinf = context["long_reinf"]
    #     N_long = context["N_long"]

    # Collect for plotting
    _main.append([main, N])
    _traverse.append([traverse, spacing])
    _long.append([long_reinf, N_long])

    if input(f"\nDesign another section! Y|N :").upper() == "Y":
        n += n
    else:
        break


# =================================================================
## Plotting
# =================================================================
print(f"\n[INFO] Lay Rebars")
plot = Plot()

sections_fig = []
for i in range(len(_main)):

    (
        print(
            f"\nSection {i+1} : \nmain reinf: {_main[i][1]}-ø{_main[i][0]}mm, \nTraverse: ø{_traverse[i][0]}mm @ {_traverse[i][1]}m, \nlong reinf: {_long[i][1]}-ø{_long[i][0]}"
        )
    )
    context = section.reinforce_details(rebar_object)
    fig = plot.plot_rec_section(context, _long[i][0], covering=2.5)

    sections_fig.append(fig)

plot.create_html(curve_fig, sections_fig)


"""
python app/deep.py
"""
