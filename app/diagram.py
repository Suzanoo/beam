## Code adapted from Prof. Fredy Gabriel Ramírez Villanueva repository
## https://github.com/SirPrime/MatrixAnalysis-Beams.git

## Tutorial: YouTube Channel วิเคราะห์โครงสร้าง กับ อ.กิจ
## https://www.youtube.com/watch?v=hCmXwMQWafk&list=LL&index=6&t=3642s

import numpy as np

from utils import xi_coordinate
from plot_curve import plot_combined

np.set_printoptions(precision=3)


# =========================================================================================
# Preprocess
## Bernoulli beam
class BeamB:
    """We define a beam section.
    E: Modulus of elasticity
    I: Inertia of the cross section
    L: Span length"""

    def __init__(self, E, I, L):
        """ATTRIBUTES:
        self.E: Modulus of elasticity
        self.I: Inertia of the cross section
        self.L: Span length
        self.k: stiffness matrix of the span"""
        self.E = E
        self.I = I
        self.L = L

        # Element stiffness matrix
        self.k = (
            E
            * I
            / L**3
            * np.array(
                [
                    [12.0, 6 * L, -12, 6 * L],
                    [6 * L, 4 * L**2, -6 * L, 2 * L**2],
                    [-12, -6 * L, 12, -6 * L],
                    [6 * L, 2 * L**2, -6 * L, 4 * L**2],
                ]
            )
        )


## Loads Name
class Load:
    """Clase Load"""

    def __init__(self, type):
        """
        type = 0: Point Load
        type = 1: Distributed Load
        type = 2: Concentrated Momento
        """
        self.type = type

    def type(self):
        if self.type == 0:
            print("Point Load")
        elif self.type == 1:
            print("Distributed Load")
        elif self.type == 2:
            print("Concentrated Momento")
        else:
            print("Undefined")


## Point Load
class PointLoad(Load):
    """Point load class"""

    def __init__(self, P=0, a=0):
        """Point load P.
        P: Load value. Positive down.
        a: Load position with respect to the left end of the section"""
        Load.__init__(self, 0)
        self.P = P
        self.a = a

    def __str__(self):
        return (
            "Point Load\n   Value= "
            + str(self.P)
            + "N"
            + "\n   Position, x= "
            + str(self.a)
            + "m"
        )

    # Qf = [Fy1, M1, Fy2, M2, ...]
    def Qf(self, L):
        """Equivalent nodal reactions for a point Load.
        L: Beam length"""
        a = self.a
        b = L - a
        return (
            self.P
            / L**2
            * np.array(
                [
                    [b**2 / L * (3 * a + b)],  # RL
                    [a * b**2],  # ML
                    [a**2 / L * (a + 3 * b)],  # RR
                    [-(a**2) * b],  # MR
                ]
            )
        )

    # Shear force in a section (beam without supports)
    def FQ(self, x, L):
        """Contribution to the shear force in a section due to a point Load,
        x: position of the section considered with respect to the extreme left
        L: span length"""
        if self.a < x <= L:
            return -self.P
        else:
            return 0

    # Bending moment in a section (simply supported beam)
    def MF(self, x, L):
        """Contribution to the bending moment in a section due to a punctual Load,
        x: position of the section considered with respect to the extreme left
        L: span length"""
        if 0 <= x < self.a:
            return (1 - self.a / L) * self.P * x
        elif x <= L:
            return self.a * self.P * (1 - x / L)
        else:
            return 0


# Distributed load
class DistributedLoad(Load):
    """Distributed load class"""

    def __init__(self, q=0, a=0, l=0):
        """distribbuted load q.
        q: load value. Positive down.
        a: distance between the left end of the span and the start of the load.
        l: length of distributed load"""
        Load.__init__(self, 1)
        self.q = q
        self.a = a
        self.l = l

    def __str__(self):
        return (
            "Load distribution\n   Value= " + str(self.q) + "N/m"
            ", "
            + "\n   Beginning= "
            + str(self.a)
            + "m"
            + "\n   Longitud= "
            + str(self.l)
            + "m"
        )

    # Qf = [RL, ML, RR, MR]
    def Qf(self, L):
        """Equivalent Nodal Reactions for a Load
        evenly distributed.
        L: beam length"""
        q = self.q
        a = self.a
        b = L - self.a - self.l
        return (
            q
            * L
            / 2
            * np.array(
                [
                    [
                        1
                        - a / L**4 * (2 * L**3 - 2 * a**2 * L + a**3)
                        - b**3 / L**4 * (2 * L - b)
                    ],
                    [
                        L
                        / 6
                        * (
                            1
                            - a**2 / L**4 * (6 * L**2 - 8 * a * L + 3 * a**2)
                            - b**3 / L**4 * (4 * L - 3 * b)
                        )
                    ],
                    [
                        1
                        - a**3 / L**4 * (2 * L - a)
                        - b / L**4 * (2 * L**3 - 2 * b**2 * L + a**3)
                    ],
                    [
                        -L
                        / 6
                        * (
                            1
                            - a**3 / L**4 * (4 * L - 3 * a)
                            - b**2 / L**4 * (6 * L**2 - 8 * b * L + 3 * b**2)
                        )
                    ],
                ]
            )
        )

    # Shear force in a section (unsupported beam)
    def FQ(self, x, L):
        """Contribution to the shear force in a section due to the distributed load.
        x: position of the section considered with respect to the extreme left
        L: Span length"""
        if self.a <= x < self.a + self.l:
            return -self.q * (x - self.a)
        # elif x <= L:
        #     return -self.q * self.l
        elif x > self.a + self.l:
            return -self.q * self.l
        else:
            return 0

    # Bending moment in a section (simply supported beam)
    def MF(self, x, L):
        """Contribution to the shear force in a section due to the distributed load.
        x: position of the section considered with respect to the extreme left
        L: Span length"""
        V1 = self.q * self.l / L * (L - self.a - self.l / 2)
        V2 = self.q * self.l - V1
        if 0 <= x < self.a:
            return V1 * x
        elif x <= self.a + self.l:
            return V1 * x - 0.5 * self.q * (x - self.a) ** 2
        elif x <= L:
            return V2 * (L - x)
        else:
            return 0

    def Δx(self, x, L):
        pass


# Concentrated moment
class MomentConcentrated(Load):
    """Clase momento concentrado"""

    def __init__(self, M=0, a=0):
        """Concentrated moment M.
        M: value of the concentrated moment. Positive counterclockwise
        a: position of the moment with respect to the left end of the section"""
        Load.__init__(self, 2)
        self.M = M
        self.a = a

    def __str__(self):
        return (
            "Moment concentrate\n   Value= "
            + str(self.M)
            + "Nm"
            + "\n   Posición, x= "
            + str(self.a)
            + "m"
        )

    # Qf = [Fy1, M1, Fy2, M2,...]
    def Qf(self, L):
        """Equivalent nodal reactions for a concentrated moment.
        L: beam length"""
        a = self.a
        b = L - a
        return (
            self.M
            / L**2
            * np.array(
                [
                    [-6 * a * b / L],
                    [b * (b - 2 * a)],
                    [6 * a * b / L],
                    [a * (a - 2 * b)],
                ]
            )
        )

    # Shear force in a section (beam without supports)
    def FQ(self, x, L):
        """Contribution to the shear force in a section due to the distributed load.
        x: position of the section considered with respect to the extreme left"""
        return 0

    # Bending moment in a section (simply supported beam)
    def MF(self, x, L):
        """Contribution to the bending moment in a section due to a concentrated moment,
        These values correspond to that of a simply supported beam.
        x: position of the section considered with respect to the extreme left
        L: Span length"""
        if 0 <= x < self.a:
            return self.M / L * x
        elif self.a < x <= L:
            return self.M * (x / L - 1)
        else:
            return 0


# =========================================================================================
# Method
## displacement matrix : di = ['d1y', 'θ1', 'd2y', 'θ2', 'd3y', 'θ3',...]
def nodal_displacement(list_of_suport):
    # "0" : "Embedement",
    # "1" : "Allows vertical scroll",
    # "2" : "Allow rotation but no scroll",
    # "3" : "Cantilever"
    d = []
    for i in range(0, len(list_of_suport)):
        if list_of_suport[i] == 0:  # fixed
            d.append(0)
            d.append(0)
        elif list_of_suport[i] == 1:  # vert-scroll
            d.append("d" + str(i + 1))
            d.append(0)
        elif list_of_suport[i] == 2:  # pin
            d.append(0)
            d.append("θ" + str(i + 1))
        elif list_of_suport[i] == 3:  # free
            d.append("d" + str(i + 1))
            d.append("θ" + str(i + 1))
        else:
            pass

    print(f"\nNodal displacement matrix \nd = {d}")
    return d


## Reaction matrix : R = ['F1y', 'M1', 'F2y', 'M2', 'F3y', 'M3',...]
def nodal_external_force(list_of_suport, R0):
    R = []
    for i in range(0, len(list_of_suport)):
        if list_of_suport[i] == 0:  # fixed
            R.append("F" + str(i + 1))
            R.append("M" + str(i + 1))
        elif list_of_suport[i] == 1:  # vert-roller
            R.append(0)
            R.append("M" + str(i + 1))
        elif list_of_suport[i] == 2:  # pinned
            R.append("F" + str(i + 1))
            R.append(0)
        elif list_of_suport[i] == 3:  # free
            R.append(0)
            R.append(0)
        else:
            pass

    if len(R0) != 0:
        for i in range(0, len(R)):
            if R0[i] != 0:
                R[i] = R0[i]

    print(f"\nNodal reaction matrix \nR = {R}")
    return R


## Stiffness matrix
## Assembly of the global stiffness matrix
def global_stiffness(nodes, spans, stretch):
    K = np.zeros((2 * nodes, 2 * nodes))
    for i in range(spans):
        K[2 * i : 2 * i + 4, 2 * i : 2 * i + 4] += stretch[i].k
    print(f"Stiffness matrix : K")
    print(f"{K}")

    return K


## Fixed-End Force
# Local fixed-end force
# Equivalent nodal reactions in each stretch
def local_FEF(b, loads, stretch):  # b = Number of stretchs or bars
    QF = [
        0
    ] * b  # placholder to save the equivalent nodal reaction vectors of each stretch
    for i in range(b):  # go through all the stretches
        for j in range(len(loads[i])):  # consider all the loads of each stretch
            QF[i] += loads[i][j].Qf(stretch[i].L)

    return QF


## Assembly the global fixed-end force
def global_FEF(nodes, b, QF):  # b = Number of stretchs or bars
    Qf = np.zeros((2 * nodes, 1))
    for i in range(b):
        Qf[2 * i : 2 * i + 4, :] += QF[i]
    print(f"\nGlobal Fixend Force, Qf :")
    print(f"{Qf}")
    return Qf


# Calculated unknown nodal displacement
"""
If we know R, we don't know d.
If we know d, we don't know R.
[Ri] = [Ki][di]+[Qfi]
R = ['0', '0', 'F2y', '0', 'F3y', 'M3', ...] --example
d = ['d1', 'θ1', '0', 'θ2', '0', '0', ...] --example
calculate d1, θ1, θ2,... exclude known == 0, 0, ...
"""


# Calculate nodal displacement
def displacement(d, K, Qf, R):
    """d : list of displacement vector
    K : np.array of global stiffness
    Qf : np.array of global FEF
    R = list of nodal external force/reaction
    """
    # index of unknowm displacement
    J = np.where(np.array(d) != "0")[0].tolist()

    # index of reaction matched unknowm displacement
    I = J

    R1 = np.zeros((len(J), 1), dtype=float)  # --->Matrix [Ri]

    # Assembly Ki matched index
    K1 = np.zeros((len(I), len(J)))
    for i in range(0, len(I)):
        for j in range(0, len(J)):
            K1[i][j] = K[I[i]][J[j]]  # --->Matrix [Ki]

    # Assembly Qfi index
    Q01 = []
    for item in I:
        q01 = [Qf[item][0]]
        Q01.append(q01)
    Q01 = np.array(Q01)  # --->Matrix [Qfi]

    # Assembly R index
    for i in range(0, len(I)):
        R1[i][0] = R[I[i]]

    # Calculate displacement
    # [di] = inv[Ki][Ri]+(-1*[Qfi])
    K1 = np.linalg.inv(K1)  # inverse[K1]

    # unknown displacement
    di = np.dot(K1, R1 + (-1 * Q01))  # dot matrix

    return di  # disp = m, θ = radian


# Calculated Nodal Reaction
# [R] = [K][d] + [Qf]
def reaction(d, di, K, Qf):
    # index of d where di will be added
    ii = np.where(np.array(d) != "0")[0].tolist()

    # added di to displacement d-matrix
    for i in range(len(ii)):
        d[ii[i]] = di[i][0]

    # Convert to array(ix1)
    dy = np.array(d).reshape(-1, 1)
    print(f"Nodal Displacement, [d] : d1, θ1, d2, θ2, ...:")
    print(f"{dy} m, radian, m, radian,...")

    # Calculated nodal reaction
    R = np.dot(K, dy) + Qf  # dot matrix

    print(f"\nExternal Force/Nodal Reaction, [R] : F1, M1, F2, M2, ... :")
    print("[R] = [K][d] + [Qf]")
    print(f"{R/1000} kN, kN-m, kN, kN-m,...")
    return dy, R


# Calculated internal force
def internal_force(dy, b, QF, stretch):
    """
    dy : np.array of displacement
    b : spans q'ty
    QF : local FEF
    """
    # Nodal displacements by stretch
    u = []
    for i in range(b):
        u.append(dy[2 * i : 2 * i + 4, :])
        # print(f"Local displacement: span {i+1} = {u[-1]} m, radian, m, radian,...")

    # Forces in each stretch
    # [Fi] = [ki][ui]+[QFi]
    F = []
    for i in range(b):
        F.append(stretch[i].k @ u[i] + QF[i])
        # print(f"Loacal force span {i+1} = {F[-1]} N, N-m, N, N-m,...")

    return u, F


# Calculate shear force values
def shears(spans, stretch, loads, F):
    numS, Xt = xi_coordinate(spans, stretch)
    Shears = []
    for i in range(spans):  # for each stretch
        # Shear like unsupported beams(Internal Shear)
        Q0 = np.zeros(numS)
        for j in range(len(loads[i])):  # consider all the loads of each stretch
            m = 0  # para enumerar las secciones
            for x in Xt[i]:  # to list the sections
                Q0[m] += loads[i][j].FQ(x, stretch[i].L)  # Calculate Qi given xi
                m += 1

        # Shear at the extreme left, obtained from the calculation
        Q1 = F[i][0]

        # Total shear
        Shears.append(Q0 + Q1)

    # Maximum and minimum shear force values (in each stretch)
    maxShear = []  # Maximum shear for each stretch
    minShear = []  # Minimal shear for each stretch
    XmaxQ = []  # locations of the maxima in each stretch
    XminQ = []  # locations of the minimum in each stretch

    print(f"\nSHEAR")
    for i in range(spans):
        maxQ = max(Shears[i])  # Máximo Shearnte
        minQ = min(Shears[i])  # Mínimo Shearnte
        print(f"Span {i+1} : maxQ = {maxQ/1000:.2f}, minQ = {minQ/1000:.2f} ,kN")

        maxShear.append(maxQ)
        minShear.append(minQ)
        indMaxQ = np.where(Shears[i] == maxQ)[0][0]  # index of maximum shear
        indMinQ = np.where(Shears[i] == minQ)[0][0]  # index of minimum shear
        XmaxQ.append(Xt[i][indMaxQ])  # location of maximum shear
        XminQ.append(Xt[i][indMinQ])  # location of minimum shear
        print(f"At location x = {Xt[i][indMaxQ]:.2f}, {Xt[i][indMinQ]:.2f} ,m")

    # Shear Force Values for Charts
    DFQ = []
    for i in range(spans):
        # Values for list type DFQ
        # Shear = (Shears[i]).tolist() # We go to kN and we convert to list, N
        Shear = (Shears[i] / 1000).tolist()  # We go to kN and we convert to list, kN
        DFQ += Shear

    return DFQ, maxShear, minShear, XmaxQ, XminQ


# Calculate bending moment values
def moments(spans, stretch, loads, F):
    numS, Xt = xi_coordinate(spans, stretch)
    Moments = []
    for i in range(spans):  # for each stretch
        # Moments like stretchs simply supported
        M0 = np.zeros(numS)
        for j in range(len(loads[i])):  # consider all the loads of each stretch
            m = 0  # to list the sections
            for x in Xt[i]:  # go through the sections
                M0[m] += loads[i][j].MF(x, stretch[i].L)
                m += 1

        # Moments due to embedment or continuity of the beam
        M1 = -F[i][1] + (F[i][3] + F[i][1]) / stretch[i].L * Xt[i]

        # Total moment
        Moments.append(M0 + M1)

    # Maximum and minimum bending moment values (in each stretch)
    maxMoment = []  # Maximum moment in each stretch
    minMoment = []  # Minimum moment in each stretch
    XmaxF = []  # locations of maximum moments by stretch
    XminF = []  # locations of the minimum moments by stretch
    print(f"\nMOMENT")
    for i in range(spans):
        maxF = max(Moments[i])  # Máximo flector
        minF = min(Moments[i])  # Mínimo flector
        print(f"Span {i+1} : maxF = {maxF/1000:.2f}, minF = {minF/1000:.2f} ,kN-m")

        maxMoment.append(-maxF)
        minMoment.append(-minF)
        indMaxF = np.where(Moments[i] == maxF)[0][0]  # index of maximum bending
        indMinF = np.where(Moments[i] == minF)[0][0]  # index of minimum bending
        XmaxF.append(Xt[i][indMaxF])  # location of maximum bending
        XminF.append(Xt[i][indMinF])  # location of minimum bending
        print(f"At location x = {Xt[i][indMaxF]:.2f}, {Xt[i][indMinF]:.2f} ,m")

    # Bending moment values for graphs
    DMF = []
    for i in range(spans):
        Flex = (-1 * Moments[i] / 1000).tolist()  # ***
        DMF += Flex

    return DMF, maxMoment, minMoment, XmaxF, XminF


def calculate_gradients(moments, X_total):
    gradients = np.gradient(moments, X_total)
    return gradients


# Define the function to find turning points
def find_turning_points(gradients, X_total):
    zero_crossings = np.where(np.diff(np.sign(gradients)))[0]
    turning_points = X_total[zero_crossings]
    print(f"Turning points : {np.array(turning_points)}")
    return turning_points


# Calculate deflection values
def deflections(moments, stretch):
    spans = len(stretch)
    total_length = sum([s.L for s in stretch])
    numS, Xt = xi_coordinate(spans, stretch)

    X_total = np.concatenate(Xt) + np.repeat(
        np.cumsum([0] + [s.L for s in stretch[:-1]]), numS
    )

    gradients = calculate_gradients(moments, X_total)
    turning_points = find_turning_points(gradients, X_total)

    deflection = np.zeros(len(X_total))

    for j in range(1, len(X_total)):
        xi = X_total[j]

        # Find the nearest turning point before the current xi
        xt = turning_points[turning_points <= xi]
        if len(xt) == 0:
            xt = 0
        else:
            xt = xt[-1]

        if xi <= xt:
            if gradients[j] >= 0:
                deflection[j] = np.trapz(moments[: j + 1], X_total[: j + 1])
            else:
                deflection[j] = np.trapz(moments[: j + 1], X_total[: j + 1])
        else:
            if gradients[j] < 0:
                deflection[j] = np.trapz(
                    moments[: np.where(X_total == xt)[0][0] + 1],
                    X_total[: np.where(X_total == xt)[0][0] + 1],
                ) - np.trapz(
                    moments[np.where(X_total == xt)[0][0] : j + 1],
                    X_total[np.where(X_total == xt)[0][0] : j + 1],
                )
            else:
                deflection[j] = np.trapz(
                    moments[: np.where(X_total == xt)[0][0] + 1],
                    X_total[: np.where(X_total == xt)[0][0] + 1],
                ) - np.trapz(
                    moments[np.where(X_total == xt)[0][0] : j + 1],
                    X_total[np.where(X_total == xt)[0][0] : j + 1],
                )

        deflection[j] = -1 * deflection[j] * 1e-5
    return deflection


# =========================================================================================
#### E, I, spans, support, loads, R
def main(E, I, spans, support_type, loads, R0):
    """
    E in GPa
    I in m4
    spans :  list of length of each span in meters
    support_type : list of support type
    loads : list of loads
    R0 : list of nodal external loads
    """
    print("PROPERTIES :")
    print(f"Es = {E*1e3:.2f} MPa, I = {I*1e8:.2f} cm4")

    # ----------------------------------------------------
    print(f"\nGEOMETRY :")
    # Define length of each span
    for i in range(len(spans)):
        print(f"Span {i+1} : {spans[i]:.2f} m")

    # ----------------------------------------------------
    print(f"\nSUPPORT :")
    support = {
        "0": "Embedement",
        "1": "Allows vertical scroll",
        "2": "Allow rotation but no scroll",
        "3": "Cantilever",
    }
    # Define list of support type
    leftSupport = support_type[0]
    rightSupport = support_type[-1]
    for i in range(len(spans) + 1):
        print(f"Support {i+1} = {support.get(str(support_type[i]))}")

    # ----------------------------------------------------
    print(f"\nNODAL EXTERNAL FORCE, Ro :")
    # Define known/unknown vector of external force/reaction (+Up, -Down)
    # R0 = ['F1y', 'M1', 'F2y', 'M2', 'F3y', 'M3',...]
    # ex. R0 = [0, 0, 0, 0, 0, 0] #N, N-m
    print(f"[Ro] = ['F1y', 'M1', 'F2y', 'M2', 'F3y', 'M3',...]")
    print(f"[Ro] = {R0}  N, N-m...")

    # ----------------------------------------------------
    print(f"\nBERNOULLI BEAM :")
    # Define the stretchs of the continuous beam in a list
    # BeamB(Elasticity, Inertia, Length) for each stretch
    stretch = []
    for i in range(len(spans)):
        st = BeamB(E, I, spans[i])
        print(f"K{i+1}")
        print(f"{st.k}")
        stretch.append(st)

    # ----------------------------------------------------
    print(f"\nLOAD:")
    # Define loads in each stretch
    """
    q = DistributedLoad (value, start, length), distance between the left end of the span and the start of the load, Down+ Up-
    P = PointLoad(value, position), Load position with respect to the left end of the section, Down+ Up-
    M = MomentConcentrated (value, position), position of the moment with respect to the left end of the section', counterclockwise+
    """

    # print load
    for i in range(0, len(loads)):
        print(f"Load in stretch {i+1} : ")
        print(*loads[i], sep="\n")

    # Number of stretchs or bars
    num_of_spans = len(stretch)

    # Number of nodes
    nodes = num_of_spans + 1

    # Total length of the beam
    Ltotal = 0
    for i in range(num_of_spans):
        Ltotal += stretch[i].L

    # ----------------------------------------------------
    print(f"\nCALCULATION :")
    # Assembly Global Stiffness, K
    K = global_stiffness(nodes, num_of_spans, stretch)

    # Calculate and assembly Fixed End Force (FEF)
    QF = local_FEF(num_of_spans, loads, stretch)
    Qf = global_FEF(nodes, num_of_spans, QF)

    # Create displacement matrix & reaction matrix
    Ro = nodal_external_force(support_type, R0)  # list
    d = nodal_displacement(support_type)  # list

    # Calculate unknown displacement
    di = displacement(d, K, Qf, Ro)

    print(f"\nMerge displacement and calculate reaction :")
    dy, R = reaction(d, di, K, Qf)

    # Calculate local displacement and local force
    u, F = internal_force(dy, num_of_spans, QF, stretch)

    # ----------------------------------------------------
    # Calculate shears coordinate for plotting
    shearDFQ, maxShear, minShear, XmaxQ, XminQ = shears(num_of_spans, stretch, loads, F)

    ###### Calculate moments coordinate for plotting
    momentDMF, maxMoment, minMoment, XmaxF, XminF = moments(
        num_of_spans, stretch, loads, F
    )

    # deflectionDFQ = deflections(momentDMF, stretch)

    fig = plot_combined(
        num_of_spans,
        Ltotal,
        stretch,
        shearDFQ,
        momentDMF,
        # deflectionDFQ,
        maxShear,
        minShear,
        XmaxQ,
        XminQ,
        maxMoment,
        minMoment,
        XmaxF,
        XminF,
    )

    print(
        "========================================================================================="
    )
    print("Any comment --> highwaynumber12@gmail.com")

    return fig


# =========================================================================================
### DESIGN ###
##  Example from URL : https://learnaboutstructures.com/sites/default/files/images/3-Frames/Det-Beam-Example-Moment.png
##  Recheck :  https://platform.skyciv.com/beam

"""

"""
E = 200  # GPa
I = (1000 * np.power(24, 3)) * 1e-8  # m4

spans = [3, 3, 3, 3, 3]

# fixd=0, vert-scroll=1, pin=2, free=3
support = [2, 0, 0, 0, 0, 2]


R0 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Load in stretch 1
# P1 = PointLoad(20000, 5) # Down+ Up-
# m1 = MomentConcentrated(-30000, 5)#counterclockwise +

q1 = DistributedLoad(173000, 0, 3)  # Down+ Up-
q2 = DistributedLoad(173000, 0, 3)
q3 = DistributedLoad(173000, 0, 3)
q4 = DistributedLoad(173000, 0, 3)
q5 = DistributedLoad(173000, 0, 3)


f1 = [q1]  # Load in stretch 1
f2 = [q2]  # Load in stretch 2
f3 = [q3]  # Load in stretch 3...
f4 = [q4]
f5 = [q5]
loads = [f1, f2, f3, f4, f5]

if __name__ == "__main__":
    main(E, I, spans, support, loads, R0)


# python app/diagram.py
