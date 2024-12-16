import numpy as np


class SectionGenerator:
    def __init__(self, materials, geometry, reinforcement):
        self.materials = materials
        self.geometry = geometry
        self.reinforcement = reinforcement

        self.𝜙b = 0.9
        self.𝜙v = 0.85

        self.materials.beta_one()

    # 3) Effective depth of section
    def eff_depth(self, covering):  # mm, mm, cm
        self.d1 = (
            covering
            + self.reinforcement.traverse_dia / 10
            + self.reinforcement.main_dia / 10 / 2
        )  # Effective depth of Compression Steel
        self.d = self.geometry.h - self.d1  # Effective depth of Tension Steel
        print(f"\nEffective Depth : \nd = {self.d:.2f} cm, d' = {self.d1:.2f} cm")

    # 4) Percent Reinforcement of section
    def percent_reinf(self):
        self.pmin = max(
            np.sqrt(self.materials.fc) / (4 * self.materials.fy),
            1.4 / self.materials.fy,
        )
        self.pb = (
            (0.85 * self.materials.fc / self.materials.fy)
            * self.materials.β1
            * (600 / (600 + self.materials.fy))
        )
        self.pmax1 = 0.75 * self.pb
        self.p = 0.50 * self.pb  # conservative!!!
        print(f"\n% Reinforcement : \npmin = {self.pmin:.4f}, pmax = {self.pmax1:.4f}")

    # 5) Section capacity
    def capacity(self):
        As = self.p * self.geometry.b * self.d  # cm2
        a = As * self.materials.fy / (0.85 * self.materials.fc * self.geometry.b)  # cm.
        self.𝜙Mn1 = self.𝜙b * As * self.materials.fy * (self.d - a / 2) * 1e-3  # kN-m

        print(f"\nSection capacity : \n𝜙Mn = {self.𝜙Mn1:.2f} kN-m")

    def section_properties(self, covering):
        self.eff_depth(covering)
        self.percent_reinf()
        self.capacity()

    def reinforce_details(self, rebar_object):
        # Step 3: Define reinforcement details
        bottom_layers, top_layers, middle_rebars = rebar_object.rebar_laying()
        context = {
            "materials": self.materials,
            "geometry": self.geometry,
            "reinforcement": self.reinforcement,
            "bottom_layers": bottom_layers,
            "top_layers": top_layers,
            "middle_rebars": middle_rebars,
        }
        return context
