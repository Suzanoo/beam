# OOP for Torsion
import numpy as np

from shear import ShearCapacity
from rebar import Rebar

rebar = Rebar


class Torsion:
    def __init__(self, fc, fv, fy, fyv, fyt, Vu, Tu):
        self.fc = fc  # MPa
        self.fv = fv  # Mpa
        self.fy = fy  # Mpa
        self.fyv = fyv  # Mpa
        self.fyt = fyt  # Mpa

        self.Tu = Tu
        self.Vu = Vu

        self.𝜙v = 0.85

        self.shear = ShearCapacity(self.fc, self.fv)
        self.rebar = Rebar()

    def section_properties(self, bw, h, covering, d, dia_traverse, solid=True):
        self.𝜙Vc = self.shear.flexural_shear(bw, d)

        ds = dia_traverse / 10  # cm

        self.Aoh = (bw - 2 * (covering + ds)) * (h - 2 * (covering + ds))  # cm2
        if solid == True:
            self.Ao = 0.85 * self.Aoh  # cm2

        self.Ph = (bw + h - 4 * (covering + ds / 2)) * 2  # cm

        self.t = self.Aoh / self.Ph  # cm

        q = (self.Tu / (bw * d)) * 1e1  # N/mm2
        τ = (self.Tu / (2 * self.Ao * self.t)) * 1e3  # stress : MPa

        print(f"Thin-wall Tube & Space Truss Analogy : ")

        print(f"Enclose Area, Aoh = {self.Aoh:.2f} cm2")
        print(f"Perimeter, Ph = {self.Ph:.2f} cm")
        print(f"Thin-wall thickness = {self.t:.2f} cm")

        print(f"\nShear stress, q = {q:.2f} MPa")
        print(f"Torsion stress, τ = {τ:.2f} MPa")

        print(f"Shear capacity, 𝜙Vc = {self.𝜙Vc:.2f} kN")

    def condition(self, Acp, Pcp):
        self.𝜙Tcr = self.𝜙v * (np.sqrt(self.fc) / 3) * (Acp * Acp / Pcp) * 1e-3  # kN-m

        𝜙Tnmax = self.𝜙v * (np.sqrt(self.fc) / 12) * (Acp * Acp / Pcp) * 1e-3  # kN-m

        if (self.𝜙Tcr > (4 * self.Tu)) or (𝜙Tnmax > self.Tu):
            print(
                f"\n𝜙Tcr = {self.𝜙Tcr:.2f} kN-m, 𝜙Tnmax = {𝜙Tnmax:.2f} kN-m, Tu = {self.Tu} kN-m : No Torsion Effect!"
            )
            return False
        else:
            print(
                f"\n𝜙Tcr = {self.𝜙Tcr:.2f} kN-m, 𝜙Tnmax = {𝜙Tnmax:.2f} kN-m, Tu = {self.Tu} kN-m : Torsion Effect"
            )
            return True

    def capacity(self, Av, s, a=45):
        𝜙Tn = (self.𝜙v * 2 * self.Ao * Av * self.fy / (s * (np.tan(a)))) * 1e-3
        print(f"Torsion capacity, 𝜙Tn = {𝜙Tn:.2f} kN-m, Tu = {self.Tu} kN-m")

    def section(self, bw, d, solid=True):
        𝜙ν = (self.𝜙Vc / (bw * d)) * 1e1  # N/mm2
        𝜙τ = self.𝜙v * (2 / 3) * np.sqrt(self.fc)  # N/mm2

        vu = (self.Vu / (bw * d)) * 1e1  # N/mm2

        if self.t < self.Aoh / self.Ph:
            τu = (self.Tu / (1.7 * self.Aoh * self.t)) * 1e3  # N/mm2
        else:
            τu = (self.Tu * self.Ph / (1.7 * self.Aoh * self.Aoh)) * 1e3  # N/mm2

        if solid:
            # Solid
            if 𝜙ν + 𝜙τ >= np.sqrt(vu * vu + τu * τu):
                print(f"\n𝜙ν + 𝜙τ  >= νu^2 + τu^2 --> Solid section OK")
            else:
                print("Please revise section")
        else:
            # Thin-wall
            if 𝜙ν + 𝜙τ >= vu + τu:
                print(f"𝜙ν + 𝜙τ  >= vu + τu --> Thin-wall section OK")
            else:
                print("Please revise section")

    def traverse(self, bw, a=45):
        """
        Av : shear reinf.
        At : torsion reinf.
        Al : longitudinal tensile reinf.
        Avt : torsion-shear reinf.
        """
        𝜙Tn = self.Tu
        bw = bw * 10  # mm
        Ao = self.Ao * 1e2  # mm2

        # Traverse for shear and torsion
        Av_ratio = bw / (3 * self.fy)  # mm2/mm
        self.At_ratio = (𝜙Tn * np.tan(a) * 1e6) / (
            self.𝜙v * 2 * Ao * self.fyv
        )  # mm2/mm
        Avt_ratio = 2 * self.At_ratio + Av_ratio  # mm2/mm

        while True:
            print(f"\n[INFO]: Re-Design Traverse : ")
            dia, As = self.rebar.rebar_selected()

            ask = input("Single stirrup or Double stirrup? S|D : ").upper()
            if ask == "S":
                Avt = 2 * As * 1e2  # mm2
                label = "Single stirrup"
            else:
                Avt = 4 * As * 1e2  # mm2
                label = "Double stirrup"

            s_avt = (Avt / Avt_ratio) / 10  # cm
            smax = min(s_avt, (3 * Avt * self.fyv / bw) / 10, self.Ph / 8, 30)  # cm

            print(f"smax = min(s_avt, 3*Avt*fyv/bw, Ph / 8, 30) = {smax:.2f} cm")

            ask = input(f"Confirm! : Y/N : ").upper()
            if ask == "Y":
                s = int(input(f"Please provide spacing in cm : "))
                new_traverse = dia
                new_spacing = s
                break
            else:
                pass

        print(f"[INFO] New Traverse:  𝜙-{dia} mm @ {s} cm")
        return new_traverse, new_spacing, label

    def longitudinal_reinf(self, bw, Acp, a=45):
        bw = bw * 10  # mm
        Acp = Acp * 1e2  # mm2
        Ph = self.Ph * 10  # mm

        Al = (
            self.At_ratio * Ph * (self.fyv / self.fyt) * (1 / (np.tan(a) ** 2))
        ) * 1e-2  # cm2

        Al_ratio = (
            self.At_ratio
            if (self.At_ratio > (bw / (6 * self.fyv)))
            else bw / (6 * self.fyv)
        )

        Almin = (
            ((5 * np.sqrt(self.fc) * Acp) / (12 * self.fyt))
            - Al_ratio * Ph * (self.fyv / self.fyt)
        ) * 1e-2  # cm2

        return max(Al, Almin)

    def design(self, b, h, c, d, As_main, dia_trav, Vu, Tu):
        # Torsion reinf
        if Tu != 0:

            print(f"\n[INFO] : LONGITUDINAL REINF.")

            Acp = b * h
            Pcp = 2 * (b + h)

            torsion = Torsion(self.fc, self.fv, self.fy, self.fv, self.fy, Vu, Tu)

            torsion.section_properties(b, h, c, d, dia_trav)

            torsion.condition(Acp, Pcp)
            torsion.section(b, d)

            # New traverse
            new_traverse, new_spacing, label = torsion.traverse(b)

            # Long-reinforcment
            Al = torsion.longitudinal_reinf(b, Acp)

            print(f"\nLongitudinal reinf. for each side : ")
            no_of_long_rebar, long_reinf_dia, long_reinf_area = self.rebar.rebar_design(
                Al
            )

            # Merge flexural and torsion reinf.
            print(f"\nMerge flexural and torsion reinf : ")
            As = As_main + Al / 4
            no_of_main, main_dia, new_As = self.rebar.rebar_design(As)

            return (
                no_of_main,
                main_dia,
                new_traverse,
                new_spacing,
                label,
                no_of_long_rebar / 2,  # 2 sides of section
                long_reinf_dia,
            )
