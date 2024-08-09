import numpy as np
import matplotlib.pyplot as plt
from utils import xi_coordinate


def cubic_interpolation_deflection(L, d1, θ1, d2, θ2, M1, M2, E, I, num_points=100):
    """
    Interpolates the deflection curve for a span using cubic shape functions,
    accounting for fixed-end moments.

    Parameters:
    - L: Length of the span
    - d1: Displacement at the start of the span
    - θ1: Rotation at the start of the span
    - d2: Displacement at the end of the span
    - θ2: Rotation at the end of the span
    - M1: Fixed-end moment at the start of the span
    - M2: Fixed-end moment at the end of the span
    - E: Modulus of elasticity
    - I: Moment of inertia of the cross section
    - num_points: Number of points to use in the interpolation

    Returns:
    - x: Array of x-coordinates along the span
    - y: Array of deflections corresponding to the x-coordinates
    """
    x = np.linspace(0, L, num_points)

    # Adjust for initial and final curvature due to fixed-end moments
    if θ1 == 0:
        θ1 = -M1 * L / (2 * E * I * 1e9)  # Adjust rotation based on fixed-end moment
    if θ2 == 0:
        θ2 = -M2 * L / (2 * E * I * 1e9)  # Adjust rotation based on fixed-end moment

    # Cubic shape functions for deflection
    N1 = 1 - 3 * (x / L) ** 2 + 2 * (x / L) ** 3
    N2 = L * (x / L - 2 * (x / L) ** 2 + (x / L) ** 3)
    N3 = 3 * (x / L) ** 2 - 2 * (x / L) ** 3
    N4 = L * (-((x / L) ** 2) + (x / L) ** 3)

    y = N1 * d1 + N2 * θ1 + N3 * d2 + N4 * θ2
    return x, y


def deflection(spans, di, Qf, E, I):
    """
    -stretch: lengths of spans in meters
    -di: Node displacements, e.g., [d1, θ1, d2, θ2, d3, θ3,  ...]
    Example: θ1 = 0.01 rad, d1 = 0 mm, θ2 = -0.02 rad, d2 = -5 mm, θ3 = 0.015 rad, d3 = 3 mm
    -
    """

    # Get x-coordinates for each span
    numS, Xt = xi_coordinate(spans)

    # Initialize lists for the full beam's x-coordinates and deflections
    X_full = []
    deflection_full = []

    # Interpolate and calculate deflections for each span
    for i in range(len(spans)):
        # Current span's nodal displacements and rotations
        d1, θ1 = (di[2 * i], di[2 * i + 1])
        d2, θ2 = di[2 * i + 2], di[2 * i + 3]

        # Fixed-end moments for the current span
        M1 = Qf[2 * i + 1]
        M2 = Qf[2 * i + 3]

        # Interpolate deflection along this span
        x, y = cubic_interpolation_deflection(
            spans[i], d1, θ1, d2, θ2, M1, M2, E, I, numS
        )

        # Adjust x-coordinates to be relative to the entire beam
        if i > 0:
            x = x + sum(spans[:i])

        # Append to full lists
        X_full.extend(x)
        deflection_full.extend(y)

    return deflection_full
