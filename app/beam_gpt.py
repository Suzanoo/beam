import os
import pandas as pd

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
from plot import Plot

from utils import display_df

CURRENT = os.getcwd()

# =================================================================
## Initialized
# =================================================================
materials = MaterialProperties(fc=25, fv=235, fy=390, Es=200000)
geometry = SectionGeometry(b=20, h=40)
reinforcement = Reinforcement(main_dia=16, traverse_dia=9)

section = SectionGenerator(materials, geometry, reinforcement)
section.section_properties(covering=2.5)

loads = Loads(Mu=20, Vu=120)
rebar_object = Rebar()
shear_object = ShearReinforcement(materials)

# Display rebar df
table = os.path.join(CURRENT, "data/Deform_Bar.csv")
df = pd.read_csv(table)
display_df(df)

# =================================================================
## Design
# =================================================================
# Calculate reinforcements required
calculator = ReinforcementCalculator(section, loads)

print(f"\n[INFO] Main Reinforcement")
calculator.section_type()
calculator.main_reinf(rebar_object)

print(f"\n[INFO] Traverse Reinforcement")
while True:
    calculator.traverse_reinf(shear_object, rebar_object)
    ask = input("Try again! : Y|N : ").upper()
    if ask != "Y":
        break

# =================================================================
## Plotting
# =================================================================
print(f"\n[INFO] Rebars laying")
plot = Plot()

context = section.reinforce_details(rebar_object)
fig = plot.plot_rec_section(context, covering=2.5)
fig.show()

"""
python app/beam_gpt.py
"""
