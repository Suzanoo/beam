import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

from rebar import Rebar


import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Plot:
    def __init__(self):
        self.rebar = Rebar()

    def plot_rec_section(self, context, middle_dia, covering):
        fig = go.Figure()

        b = context["geometry"].b
        h = context["geometry"].h
        main_dia = context["reinforcement"].main_dia / 10  # Convert mm to cm
        traverse_dia = context["reinforcement"].traverse_dia / 10  # Convert mm to cm
        middle_dia = middle_dia / 10

        bottom_layers = context["bottom_layers"]
        top_layers = context["top_layers"]
        middle_rebars = context["middle_rebars"]

        self._draw_section(fig, b, h, covering, traverse_dia)
        self._draw_rebars(
            fig,
            covering,
            b,
            h,
            main_dia,
            traverse_dia,
            middle_dia,
            bottom_layers,
            top_layers,
            middle_rebars,
        )

        fig.update_xaxes(range=[-5, b + 5], scaleratio=1, zeroline=False)
        fig.update_yaxes(range=[-5, h + 5], scaleratio=1, zeroline=False)
        fig.update_layout(
            title="",
            xaxis_title="Width (cm)",
            yaxis_title="Depth (cm)",
            height=600,
            width=600,
            yaxis=dict(scaleanchor="x", scaleratio=1),
        )

        return fig

    def _draw_section(self, fig, b, h, covering, traverse_dia):
        fig.add_shape(
            type="rect",
            x0=0,
            y0=0,
            x1=b,
            y1=h,
            line=dict(color="gray", width=3),
            fillcolor="lightgray",
        )

        fig.add_shape(
            type="rect",
            x0=covering,
            y0=covering,
            x1=b - covering,
            y1=h - covering,
            line=dict(color="green", width=2),
        )

        fig.add_shape(
            type="rect",
            x0=covering + traverse_dia,
            y0=covering + traverse_dia,
            x1=b - covering - traverse_dia,
            y1=h - covering - traverse_dia,
            line=dict(color="green", width=2),
        )

    def _draw_rebars(
        self,
        fig,
        covering,
        b,
        h,
        main_dia,
        traverse_dia,
        middle_dia,
        bottom_layers,
        top_layers,
        middle_rebars,
    ):
        layer_spacing = 2 * main_dia
        # Top layers
        y_top_layers = [
            h - covering - (i + 0.5) * layer_spacing for i in range(len(top_layers))
        ]
        self._draw_rebar_layers(
            fig, covering, b, y_top_layers, top_layers, main_dia, traverse_dia
        )

        # Bottom layers
        y_bottom_layers = [
            covering + (i + 0.5) * layer_spacing for i in range(len(bottom_layers))
        ]
        self._draw_rebar_layers(
            fig, covering, b, y_bottom_layers, bottom_layers, main_dia, traverse_dia
        )

        # Middle layers
        if middle_rebars > 0:
            self._draw_middle_rebars(
                fig,
                b,
                covering,
                traverse_dia,
                middle_dia,
                y_top_layers,
                y_bottom_layers,
                middle_rebars,
            )

    def _draw_rebar_layers(
        self, fig, covering, b, y_layers, num_bars_list, main_dia, traverse_dia
    ):
        for y, num_bars in zip(y_layers, num_bars_list):
            x_positions = self.rebar.calculate_rebar_positions(
                covering, b, num_bars, main_dia, traverse_dia
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

    def _draw_middle_rebars(
        self,
        fig,
        b,
        covering,
        traverse_dia,
        middle_dia,
        y_top_layers,
        y_bottom_layers,
        middle_rebars,
    ):
        n = middle_rebars // 2
        d_middle = min(y_top_layers) - max(y_bottom_layers)
        spacing = d_middle / (n + 1)
        for i in range(1, n + 1):
            y_position = max(y_bottom_layers) + spacing * i
            fig.add_shape(
                type="circle",
                x0=covering + traverse_dia,
                y0=y_position - middle_dia / 2,
                x1=covering + traverse_dia + middle_dia,
                y1=y_position + middle_dia / 2,
                line=dict(color="blue"),
                fillcolor="blue",
            )
            fig.add_shape(
                type="circle",
                x0=b - covering - traverse_dia - middle_dia,
                y0=y_position - middle_dia / 2,
                x1=b - covering - traverse_dia,
                y1=y_position + middle_dia / 2,
                line=dict(color="blue"),
                fillcolor="blue",
            )

    def xi_coordinate(self, spans):
        numS = 1000
        Xt = [np.linspace(0, span, numS) for span in spans]
        return numS, Xt

    def x_coordinate(self, spans, stretch, Xt):
        X = []
        temp = 0
        for i, span in enumerate(spans):
            if i > 0:
                temp += stretch[i - 1].L
            X += (Xt[i] + temp).tolist()
        return X

    def plot_curve(
        self,
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
        numS, Xt = self.xi_coordinate(spans)
        X = self.x_coordinate(spans, stretch, Xt)

        invert_y = label != "Shear"
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=X, y=DFQ, mode="lines"))

        if invert_y:
            fig.update_yaxes(autorange="reversed")

        if max_values is not None:
            self._add_markers(
                fig,
                spans,
                Ltotal,
                stretch,
                max_values,
                min_values,
                Xmax_values,
                Xmin_values,
            )

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

    def _add_markers(
        self,
        fig,
        spans,
        Ltotal,
        stretch,
        max_values,
        min_values,
        Xmax_values,
        Xmin_values,
    ):
        temp = 0
        for i, span in enumerate(spans):
            if i > 0:
                temp += stretch[i - 1].L
            ubicMax = temp + Xmax_values[i]
            ubicMin = temp + Xmin_values[i]
            ubicMax = Ltotal - stretch[i].L / 2 if ubicMax == Ltotal else ubicMax
            ubicMin = Ltotal - stretch[i].L / 2 if ubicMin == Ltotal else ubicMin

            fig.add_trace(
                go.Scatter(
                    x=[ubicMax],
                    y=[max_values[i] / 1000],
                    mode="markers",
                    text=[str(round(max_values[i] / 1000, 2))],
                    textposition="top center",
                    marker=dict(color="red", size=10),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=[ubicMin],
                    y=[min_values[i] / 1000],
                    mode="markers",
                    text=[str(round(min_values[i] / 1000, 2))],
                    textposition="bottom center",
                    marker=dict(color="blue", size=10),
                )
            )

    def plot_curves(
        self,
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
        shear_fig = self.plot_curve(
            "Shear", spans, Ltotal, stretch, shearDFQ, maxShear, minShear, XmaxQ, XminQ
        )
        moment_fig = self.plot_curve(
            "Moment",
            spans,
            Ltotal,
            stretch,
            momentDFQ,
            maxMoment,
            minMoment,
            XmaxM,
            XminM,
        )
        deflection_fig = self.plot_curve(
            "Deflection", spans, Ltotal, stretch, deflectionDFQ, None, None, None, None
        )

        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(
                "Shear Force Diagram(kN)",
                "Bending Moment Diagram(kN-m)",
                "Delta by Cubic Interpolation",
            ),
        )

        for trace in shear_fig["data"]:
            fig.add_trace(trace, row=1, col=1)
        for trace in moment_fig["data"]:
            fig.add_trace(trace, row=2, col=1)
        for trace in deflection_fig["data"]:
            fig.add_trace(trace, row=3, col=1)

        fig.update_yaxes(visible=False, row=3, col=1)
        fig.update_layout(height=800, showlegend=False)

        return fig

    def create_html(self, curve_fig, sections_fig):
        if curve_fig is not None:
            curve_html = curve_fig.to_html(full_html=False, include_plotlyjs="cdn")
        else:
            curve_html = "Hello World!"

        # Start building the HTML content
        html_content = f"""
        <html>
            <head>
                <title>Sections</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <h1>SFD, BMD</h1>
                <div class="plot-curve">{curve_html}</div>
                <h1>Sections</h1>
        """

        # Loop through the list of figures, displaying 4 per row
        for i in range(len(sections_fig)):
            if i % 4 == 0:  # Start a new row every 4 sections
                if i != 0:  # Close the previous row div if it's not the first
                    html_content += "</div>"
                html_content += """<div class="plot-sections" style="display: flex; justify-content: space-around; margin-bottom: 30px;">"""

            # Convert each figure to HTML
            section_html = sections_fig[i].to_html(
                full_html=False, include_plotlyjs=False
            )

            # Add the section plot to the current row
            html_content += f"""
                <div style="width: 23%;">
                    <h2>Section-{i + 1}</h2>
                    {section_html}
                </div>
            """

        # Close the last row div
        html_content += "</div>"

        # End the HTML content
        html_content += """
            </body>
        </html>
        """

        # Write the HTML content to a file
        with open("rectangle_plot.html", "w") as f:
            f.write(html_content)

        print("Congrate! Please open rectangle_plot.html in your project folder")
