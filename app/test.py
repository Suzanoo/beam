import numpy as np
import matplotlib.pyplot as plt

# Beam properties
L1 = 10  # Length of AB (m)
L2 = 10  # Length of BC (m)
w = 2  # UDL on AB (kN/m)
P = 10  # Point load at midpoint of BC (kN)

# Discretize the beam
x1 = np.linspace(0, L1, 500)
x2 = np.linspace(0, L2, 500)

# Shear force calculation
V_AB = w * (L1 - x1)
V_BC = np.piecewise(x2, [x2 < L2 / 2, x2 >= L2 / 2], [10, 0])

# Bending moment calculation
M_AB = (w * x1 * (L1 - x1)) / 2
M_BC = np.piecewise(x2, [x2 < L2 / 2, x2 >= L2 / 2], [lambda x: 10 * (L2 / 2 - x), 0])

# Deflection calculation (simplified for illustration)
E = 200000  # Young's modulus (MPa)
I = 5000  # Moment of inertia (cm^4)

delta_AB = (w * x1**2 * (3 * L1 - x1**2)) / (24 * E * I)
delta_BC = np.piecewise(
    x2,
    [x2 < L2 / 2, x2 >= L2 / 2],
    [lambda x: (P * x**2 * (3 * L2 / 2 - x)) / (6 * E * I), 0],
)

# Plotting
plt.figure(figsize=(12, 8))

# Shear force plot
plt.subplot(3, 1, 1)
plt.plot(x1, V_AB, label="Shear force AB")
plt.plot(L1 + x2, V_BC, label="Shear force BC")
plt.axhline(0, color="black", linewidth=0.5)
plt.title("Shear Force Diagram")
plt.xlabel("Length (m)")
plt.ylabel("Shear Force (kN)")
plt.legend()

# Bending moment plot
plt.subplot(3, 1, 2)
plt.plot(x1, M_AB, label="Bending Moment AB")
plt.plot(L1 + x2, M_BC, label="Bending Moment BC")
plt.axhline(0, color="black", linewidth=0.5)
plt.title("Bending Moment Diagram")
plt.xlabel("Length (m)")
plt.ylabel("Bending Moment (kN.m)")
plt.legend()

# Deflection plot
plt.subplot(3, 1, 3)
plt.plot(x1, delta_AB, label="Deflection AB")
plt.plot(L1 + x2, delta_BC, label="Deflection BC")
plt.axhline(0, color="black", linewidth=0.5)
plt.title("Deflection Curve")
plt.xlabel("Length (m)")
plt.ylabel("Deflection (mm)")
plt.legend()

plt.tight_layout()
plt.show()
