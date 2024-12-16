# OOP for shear
import numpy as np

from rebar import Rebar


class ShearCapacity:
    def __init__(self, fc, fv):
        self.fc = fc  # MPa
        self.fv = fv  # Mpa SR24
        self.𝜙v = 0.85

    # Shear resistance of concrete
    def flexural_shear(self, bw, d):
        """
        bw : cm
        d : cm
        𝜙Vc : kN
        """
        𝜙Vc = self.𝜙v * (np.sqrt(self.fc) / 6) * bw * d * 1e-1
        return 𝜙Vc

    def axial_shear(self, Nu, Ag, bw, d):
        """
        Nu: kN
        Ag: cm2
        bw : cm
        d : cm
        𝜙Vc : kN
        """
        𝜙Vc = self.𝜙v * (1 + Nu / (14 * Ag)) * (np.sqrt(self.fc) / 6) * bw * d

    def travers(self, Av, d, s):
        """
        Av: cm2
        """
        𝜙Vs = (self.𝜙v * Av * self.fv * d / s) * 1e-1

    def bent(self, bw, d, Av, alpha):
        𝜙Vs1 = self.𝜙v * Av * self.fv * np.sin(np.radians(alpha)) * 1e-1
        𝜙Vs2 = self.𝜙v * (np.sqrt(self.fc) / 4) * bw * d * 1e-1
        𝜙Vs = np.min(𝜙Vs1, 𝜙Vs2)


class ShearReinforcement:
    def __init__(self, materials):
        self.fc = materials.fc  # MPa
        self.fv = materials.fv  # Mpa SR24
        self.fy = materials.fy  # MPa
        self.𝜙v = 0.85

    def beamTraverse(self, b, d, Av, Vu):
        """
        b: cm
        d: cm
        Av: cm2
        Vu: kN
        """
        shear = ShearCapacity(self.fc, self.fv)
        𝜙Vc = shear.flexural_shear(b, d)

        𝜙Vs = np.abs(Vu - 𝜙Vc)  # kN

        s_req = (self.𝜙v * Av * self.fv * d / 𝜙Vs) * 1e-1  # cm

        lg = (1 / 3) * self.𝜙v * np.sqrt(self.fc) * b * d * 1e-1  # light shear, kN

        hv = (2 / 3) * self.𝜙v * np.sqrt(self.fc) * b * d * 1e-1  # heavy shear, kN

        if Vu <= 𝜙Vc:
            s_max = min(3 * Av * self.fv / b, d / 2, 60)  # cm, ACI 11.5.5.3;11-13
            print("case1")
            print(f"Vu = {Vu:.2f}, 𝜙Vc = {𝜙Vc:.2f}, 𝜙Vs = 0")
            print(f"s_max = {s_max:.2f} cm")
            return s_req, s_max

        elif 𝜙Vc < Vu <= 𝜙Vc + lg:
            s_max = min(
                self.𝜙v * Av * self.fv * d / (𝜙Vs * 10), d / 2, 60
            )  # cm, ACI 11.5.6.4;11-16
            print("case2")
            print(f"Vu = {Vu:.2f}, 𝜙Vc = {𝜙Vc:.2f}, 𝜙Vs = {𝜙Vs:.2f}")
            print(f"s_max = {s_max} cm")
            return s_req, s_max

        elif 𝜙Vc + lg < Vu <= 𝜙Vc + hv:
            s_max = min(
                self.𝜙v * Av * self.fv * d / (𝜙Vs * 10), d / 4, 30
            )  # cm, ACI 11.5.6.4;11-16
            print("case3")
            print(f"Vu = {Vu:.2f}, 𝜙Vc = {𝜙Vc:.2f}, 𝜙Vs = {𝜙Vs:.2f}")
            print(f"s_max = {s_max:.2f} cm")
            return s_req, s_max

        else:
            print("case4")
            print(f"Vu = {Vu:.2f}, 𝜙Vc = {𝜙Vc:.2f}, 𝜙Vs = {𝜙Vs:.2f}")
            print("Heavy shear --> Revised cross section")
            return 0, 0

    def deepBeam(self, b, d, ln):
        """
        b: cm
        d: cm
        ln: cm
        """
        rebar = Rebar()

        """
        Step:
        -Provide spacing
        -Check A min
        -Provide A
        -Check condition of 𝜙Vn
        """

        # Traverse
        while True:
            s = int(
                input(
                    f"\nTraverse: Spacing must less than  = {d/2:.2f} and 50 cm, please try spacing in cm : "
                )
            )
            Avmin = 0.0015 * b * s
            print(f"Av min = {Avmin:.2f} cm2, please select diameter of traverse.")

            traverse_dia, Av = rebar.rebar_selected()

            ask = input("Single stirrup or Double stirrup? S|D : ").upper()
            if ask == "S":
                Av = 2 * Av  # cm2
                label = "Single stirrup"
            else:
                Av = 4 * Av
                label = "Double stirrup"

            print(f"Av = {Av:.2f} cm2")

            if Av >= Avmin:

                ask = input("Try again! : Y/N : ").upper()
                if ask == "Y":
                    pass
                else:
                    print(f"[INFO] Traverse: ø-{traverse_dia} mm @ {s} cm")
                    break
            else:
                print("Select again !!!")
                pass

        # Horizontal
        while True:
            s2 = int(
                input(
                    f"\nExtra Horizontal: Spacing must less than  = {d/3:.2f} and 50 cm, please try spacing in cm: "
                )
            )
            Avhmin = 0.0025 * b * s2
            print(
                f"Avh min = {Avhmin:.2f} cm2, please select diameter of horizontal rebar."
            )

            horizontal_dia, Avh = rebar.rebar_selected()
            Avh = 2 * Avh

            print(f"Avh = {Avh:.2f} cm2")

            if Avh >= Avhmin:

                ask = input("Try again! : Y/N : ").upper()
                if ask == "Y":
                    pass
                else:
                    print(
                        f"[INFO] Horizontal reinforcement: ø-{horizontal_dia} mm @ {s2} cm"
                    )
                    N = int((np.ceil(d / s2) - 1) * 2)
                    break
            else:
                print("Select again !!!")
                pass

        # Shear capcity
        𝜙Vs = (
            self.𝜙v
            * (
                (Av / s) * self.fv * d * ((1 + (ln / d)) / 12)
                + (Avh / s2) * self.fy * d * ((11 - ln / d) / 12)
            )
            * 1e-1
        )  # kN
        return traverse_dia, s, horizontal_dia, s2, N, 𝜙Vs, label
