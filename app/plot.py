import plotly.graph_objects as go
from plotly.subplots import make_subplots

from rebar import Rebar


from utils import xi_coordinate, X_coordinate


class Plot:
    def __init__(self):
        self.rebar = Rebar()

    def plot_rec_section(self, context, covering):

        fig = go.Figure()

        b = context["geometry"].b
        h = context["geometry"].h
        main_dia = context["reinforcement"].main_dia / 10  # Convert mm to cm
        traverse_dia = context["reinforcement"].traverse_dia / 10  # Convert mm to cm

        bottom_layers = context["bottom_layers"]
        top_layers = context["top_layers"]
        middle_rebars = context["middle_rebars"]

        # Draw the concrete section
        fig.add_shape(
            type="rect",
            x0=0,
            y0=0,
            x1=b,
            y1=h,
            line=dict(color="gray", width=3),
            fillcolor="lightgray",
        )

        # Draw the concrete cover
        fig.add_shape(
            type="rect",
            x0=covering,
            y0=covering,
            x1=b - covering,
            y1=h - covering,
            line=dict(color="green", width=2),
        )

        # Draw the traverse
        fig.add_shape(
            type="rect",
            x0=covering + traverse_dia,
            y0=covering + traverse_dia,
            x1=b - covering - traverse_dia,
            y1=h - covering - traverse_dia,
            line=dict(color="green", width=2),
        )

        # Calculate positions of top reinforcement layers
        layer_spacing = 2 * main_dia
        y_top_layers = [
            h - covering - (i + 0.5) * layer_spacing for i in range(len(top_layers))
        ]

        for y, num_bars in zip(y_top_layers, top_layers):
            x_positions = self.rebar.calculate_rebar_positions(
                covering,
                b,
                num_bars,
                main_dia,
                traverse_dia,
            )
            for x in x_positions:
                fig.add_shape(
                    type="circle",
                    x0=x - main_dia / 2,
                    y0=y - main_dia / 2,
                    x1=x + main_dia / 2,
                    y1=y + main_dia / 2,
                    line=dict(color="blue"),
                    fillcolor="blue",
                )

        # Calculate positions of bottom reinforcement layers
        y_bottom_layers = [
            covering + (i + 0.5) * layer_spacing for i in range(len(bottom_layers))
        ]

        for y, num_bars in zip(y_bottom_layers, bottom_layers):
            x_positions = self.rebar.calculate_rebar_positions(
                covering,
                b,
                num_bars,
                main_dia,
                traverse_dia,
            )
            for x in x_positions:
                fig.add_shape(
                    type="circle",
                    x0=x - main_dia / 2,
                    y0=y - main_dia / 2,
                    x1=x + main_dia / 2,
                    y1=y + main_dia / 2,
                    line=dict(color="blue"),
                    fillcolor="blue",
                )

        # Calculate positions of middle reinforcement layers
        if middle_rebars > 0:
            n = middle_rebars // 2
            d_middle = min(y_top_layers) - max(y_bottom_layers)
            s = d_middle / (n + 1)

            for i in range(1, n + 1):
                y_position = max(y_bottom_layers) + s * i
                fig.add_shape(
                    type="circle",
                    x0=covering + traverse_dia,
                    y0=y_position - main_dia / 2,
                    x1=covering + traverse_dia + main_dia,
                    y1=y_position + main_dia / 2,
                    line=dict(color="blue"),
                    fillcolor="blue",
                )
                fig.add_shape(
                    type="circle",
                    x0=b - covering - traverse_dia - main_dia,
                    y0=y_position - main_dia / 2,
                    x1=b - covering - traverse_dia,
                    y1=y_position + main_dia / 2,
                    line=dict(color="blue"),
                    fillcolor="blue",
                )

        # Set axis properties to ensure equal scale
        fig.update_xaxes(range=[-5, b + 5], scaleratio=1, zeroline=False)
        fig.update_yaxes(range=[-5, h + 5], scaleratio=1, zeroline=False)
        fig.update_layout(
            title="RC Beam Section",
            xaxis_title="Width (cm)",
            yaxis_title="Depth (cm)",
            height=600,
            width=600,
            yaxis=dict(scaleanchor="x", scaleratio=1),
        )

        return fig

    def plot_curve(
        label,
        spans,
        Ltotal,
        stretch,
        DFQ,
        max_values,
        min_values,
        Xmax_values,
        Xmin_values,
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
