class MaterialProperties:
    def __init__(self, fc, fv, fy, Es):
        self.fc = fc  # Concrete compressive strength (MPa)
        self.fv = fv  # Steel yield strength (MPa) of round bar
        self.fy = fy  # Steel yield strength (MPa) of deform bar
        self.Es = Es  # Steel elastic modulus (MPa)

    def beta_one(self):  # β1
        if self.fc <= 30:  # MPa
            self.β1 = 0.85
        elif self.fc > 30 and self.fc < 55:  # MPa
            self.β1 = 0.85 - 0.05 * (self.fc - 30) / 7
        else:
            self.β1 = 0.65

    def __str__(self):
        return f"Materials: f'c: {self.fc}, fv: {self.fv}, fy: {self.fy}, Es: {self.Es} mPa"


class SectionGeometry:
    def __init__(self) -> None:
        """ """

    def rectangle(self, b, h):
        self.b = b  # width (cm)
        self.h = h  # height (cm)

    def __str__(self):
        return f"Geometry: {self.b} x {self.h} cm"


class Reinforcement:
    def __init__(self, main_dia, traverse_dia):
        self.main_dia = main_dia  # main reinforcement (mm)
        self.traverse_dia = traverse_dia  # traverse reinforcement (mm)


class Loads:
    def __init__(self, Mu, Vu, Tu=0):
        self.Mu = Mu  # kN-m
        self.Vu = Vu  # kN
        self.Tu = Tu  # kN-m


class ReinforcementCalculator:
    def __init__(self, section, loads):
        self.materials = section.materials
        self.geometry = section.geometry
        self.reinforcement = section.reinforcement
        self.loads = loads

        self.phi_b = section.𝜙b
        self.d = section.d
        self.d1 = section.d1
        self.pmin = section.pmin
        self.pmax1 = section.pmax1
        self.phi_Mn1 = section.𝜙Mn1

    def calculate_ru(self):
        return abs(self.loads.Mu) * 1000 / (self.geometry.b * self.d**2)

    def calculate_p_req(self, Ru):
        fc, fy = self.materials.fc, self.materials.fy
        return 0.85 * (fc / fy) * (1 - (1 - 2 * (Ru / self.phi_b) / (0.85 * fc)) ** 0.5)

    def section_type(self):
        phi_Mn2 = abs(self.loads.Mu) - self.phi_Mn1
        if phi_Mn2 > 0:
            self.type = "double_reinforcement"
            print("Double_reinforcement")
            print(
                f"Mu = {self.loads.Mu:.2f}, 𝜙Mn1 = {self.phi_Mn1:.2f}, 𝜙Mn2 = {phi_Mn2:.2f} :kg.m"
            )

        else:
            self.type = "singly_reinforcement"
            phi_Mn2 = 0
            print("Singly_reinforcement")

    def singly_reinforced(self):
        Ru = self.calculate_ru()
        p_req = self.calculate_p_req(Ru)

        As_major = max(p_req, self.pmin) * self.geometry.b * self.d

        print(
            f"Ru = {Ru:.2f}, p_req = {p_req:.4f}, pmin = {self.pmin:.4f}, pmax = {self.pmax1:.4f}"
        )
        print(f"As_major = {As_major:.2f} cm2, As_minor = 0 cm2")
        return As_major

    def double_reinforced(self):
        phi_Mn2 = abs(self.loads.Mu) - self.phi_Mn1
        As1 = self.pmax1 * self.geometry.b * self.d
        As2 = (phi_Mn2 * 1000 / self.phi_b) / (self.materials.fy * (self.d - self.d1))
        As_major = As1 + As2

        p1 = (As1 + As2) / (self.geometry.b * self.d)
        p2 = As2 / (self.geometry.b * self.d)

        fs, As_minor = self.calculate_double_reinf_params(p1, p2, As1, As2)

        print(f"As_major = {As_major:.2f} cm2, As_minor = {As_minor:.2f} cm2")
        return fs, As_major, As_minor

    def calculate_double_reinf_params(self, p1, p2, As1, As2):
        fc, fy, beta1 = self.materials.fc, self.materials.fy, self.materials.β1

        if p1 - p2 > 0.85 * fc * self.d1 * beta1 * (600 / (600 - fy)) / (fy * self.d):
            fs = fy
            As_minor = As2
            print(f"fs' = {fs:.2f} --> Yield: OK")

            if self.pmax1 + p2 > 1.4 / fy and self.pmax1 + p2 < p1:
                print("pmin < p < pmax ---> OK")
            else:
                print("p ---< Out of range")
        else:
            fs = 600 * (1 - (self.d1 / self.d) * (600 + fy) / 600)
            print(f"fs' = {fs:.2f} --> fs' Not Yield")

            a = beta1 * self.d * (600 / (600 + fy))
            As_minor = (As1 * fy - 0.85 * fc * a * self.geometry.b) / fs

        return fs, As_minor

    def main_reinf(self, rebar_object):
        if self.type == "singly_reinforcement":
            As_major = self.singly_reinforced()
            return rebar_object.rebar_design(As_major)

        else:
            fs, As_major, As_minor = self.double_reinforced()
            return rebar_object.rebar_design(As_major)

    # 10) Calculate traverse spacing
    def traverse_reinf(self, shear_object, rebar_object):
        dia, As = rebar_object.rebar_selected()
        ask = input("Single stirrup or Double stirrup? S|D : ").upper()
        if ask == "S":
            Av = 2 * As  # cm2
            label = "Single stirrup"
        else:
            Av = 4 * As
            label = "Double stirrup"

        s_req, s_max = shear_object.beamTraverse(
            self.geometry.b, self.d, Av, self.loads.Vu
        )

        s = float(
            input(
                f"s_req = {s_req:.2f} cm, s_max = {s_max:.2f} cm, Please select spacing : "
            )
        )

        print(f"Traverse:  ø-{dia} mm @ {s} cm")
        return int(dia), Av, s
