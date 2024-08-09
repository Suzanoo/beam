import plotly.graph_objs as go
from plotly.subplots import make_subplots

from utils import xi_coordinate, X_coordinate


def plot_diagram(
    label, spans, Ltotal, stretch, DFQ, max_values, min_values, Xmax_values, Xmin_values
):

    numS, Xt = xi_coordinate(spans)

    X = X_coordinate(spans, stretch, Xt)

    if label == "Shear":
        invert_y = False
    else:
        invert_y = True

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=X, y=DFQ, mode="lines"))

    if invert_y:
        fig.update_yaxes(autorange="reversed")

    # Texts and markers for maximum and minimum values
    def calculateMarkers(max_values, min_values, Xmax_values, Xmin_values):
        temp = 0
        annotations = []
        for i in range(len(spans)):
            if i > 0:
                temp += stretch[i - 1].L
            ubicMax = temp + Xmax_values[i]
            ubicMin = temp + Xmin_values[i]
            if ubicMax == Ltotal:
                ubicMax = Ltotal - stretch[i].L / 2
            if ubicMin == Ltotal:
                ubicMin = Ltotal - stretch[i].L / 2

            fig.add_trace(
                go.Scatter(
                    x=[ubicMax],
                    y=[max_values[i] / 1000],
                    mode="markers",
                    text=[
                        str(round(max_values[i] / 1000, 2))
                        # + lb[-1]
                        # + str(round(ubicMax, 2))
                        # + "$m$"
                    ],
                    textposition="top center",
                    marker=dict(color="red", size=10),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=[ubicMin],
                    y=[min_values[i] / 1000],
                    mode="markers",
                    text=[
                        str(round(min_values[i] / 1000, 2))
                        # + lb[-1]
                        # + str(round(ubicMin, 2))
                        # + "$m$"
                    ],
                    textposition="bottom center",
                    marker=dict(color="blue", size=10),
                )
            )

        return annotations

    if max_values != None:
        fig.update_layout(
            annotations=calculateMarkers(
                max_values, min_values, Xmax_values, Xmin_values
            )
        )

    # To shade the graph.
    Xgraf = [0] + X + [Ltotal]
    DFQgraf = [0] + DFQ + [0]

    fig.add_trace(
        go.Scatter(
            x=Xgraf,
            y=DFQgraf,
            fill="tozeroy",
            fillcolor="rgba(0, 0, 255, 0.3)",
            mode="none",
        )
    )

    return fig


# Example usage of plot_diagram for shear and moment diagrams
def plot_combined(
    spans,
    Ltotal,
    stretch,
    shearDFQ,
    momentDFQ,
    maxShear,
    minShear,
    XmaxQ,
    XminQ,
    maxMoment,
    minMoment,
    XmaxM,
    XminM,
    deflectionDFQ,
):
    shear_fig = plot_diagram(
        "Shear", spans, Ltotal, stretch, shearDFQ, maxShear, minShear, XmaxQ, XminQ
    )
    moment_fig = plot_diagram(
        "Moment", spans, Ltotal, stretch, momentDFQ, maxMoment, minMoment, XmaxM, XminM
    )

    deflection_fig = plot_diagram(
        "Deflection",
        spans,
        Ltotal,
        stretch,
        deflectionDFQ,
        None,
        None,
        None,
        None,
    )

    # Create subplots
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        # subplot_titles=("Shear Force Diagram(kN)", "Bending Moment Diagram(kN-m)"),
        subplot_titles=(
            "Shear Force Diagram(kN)",
            "Bending Moment Diagram(kN-m)",
            "Delta by Cubic Interpolation",
        ),
    )

    # Add shear force diagram
    for trace in shear_fig["data"]:
        fig.add_trace(trace, row=1, col=1)

    # Add moment diagram
    for trace in moment_fig["data"]:
        fig.add_trace(trace, row=2, col=1)

    # Add deflection

    for trace in deflection_fig["data"]:
        fig.add_trace(trace, row=3, col=1)

    fig.update_layout(height=800, showlegend=False)

    fig.show()

    return fig
