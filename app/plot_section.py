import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd


# typical layer position : -EQ-EQ-EQ-
def calculate_rebar_positions(c, b, N, main_dia, travesre_dia):
    if N == 1:
        return [c + (b - 2 * c) / 2]
    elif N == 2:
        return [c + travesre_dia + main_dia / 2, b - c - travesre_dia - main_dia / 2]
    else:
        positions = [
            c
            + main_dia / 2
            + travesre_dia
            + i * (b - 2 * c - main_dia - 2 * travesre_dia) / (N - 1)
            for i in range(N)
        ]
        return positions


# Calculate coordinates of rebars
def get_rebar_coordinates(
    b,
    d,
    c,
    main_dia,
    travesre_dia,
    middle_dia,
    bottom_layers,
    top_layers,
    middle_rebars,
):
    rebar_data = []

    # Calculate positions of bottom reinforcement layers
    layer_spacing = 2 * main_dia
    y_bottom_layers = [c + (i + 0.5) * layer_spacing for i in range(len(bottom_layers))]

    for y, num_bars in zip(y_bottom_layers, bottom_layers):
        x_positions = calculate_rebar_positions(c, b, num_bars, main_dia, travesre_dia)
        for x in x_positions:
            z = d - y
            rebar_data.append({"x": x, "y": y, "z": z})

    # Calculate positions of top reinforcement layers
    y_top_layers = [d - c - (i + 0.5) * layer_spacing for i in range(len(top_layers))]

    for y, num_bars in zip(y_top_layers, top_layers):
        x_positions = calculate_rebar_positions(c, b, num_bars, main_dia, travesre_dia)
        for x in x_positions:
            z = d - y
            rebar_data.append({"x": x, "y": y, "z": z})

    # Calculate positions of middle reinforcement layers
    if middle_rebars > 0:
        n = middle_rebars // 2
        d_middle = min(y_top_layers) - max(y_bottom_layers)
        s = d_middle / (n + 1)

        for i in range(1, n + 1):
            y_position = max(y_bottom_layers) + s * i
            z = d - y_position
            rebar_data.append(
                {"x": c + travesre_dia + middle_dia / 2, "y": y_position, "z": z}
            )
            rebar_data.append(
                {"x": b - c - travesre_dia - middle_dia / 2, "y": y_position, "z": z}
            )

    return pd.DataFrame(rebar_data)


def section_fig(
    fig,
    b,
    d,
    c,
    main_dia,
    travesre_dia,
    middle_dia,
    bottom_layers,
    top_layers,
    no_of_middle_rebars,
    legend,
):
    # fig = go.Figure()

    # Draw the concrete section
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=b,
        y1=d,
        line=dict(color="gray", width=3),
        fillcolor="lightgray",
    )

    # Draw the concrete cover
    fig.add_shape(
        type="rect",
        x0=c,
        y0=c,
        x1=b - c,
        y1=d - c,
        line=dict(color="red", width=2, dash="dot"),
    )

    # Draw the traverse
    fig.add_shape(
        type="rect",
        x0=c + travesre_dia,
        y0=c + travesre_dia,
        x1=b - c - travesre_dia,
        y1=d - c - travesre_dia,
        line=dict(color="red", width=2, dash="dot"),
    )

    # Calculate positions of bottom reinforcement layers
    layer_spacing = 2 * main_dia
    y_bottom_layers = [c + (i + 0.5) * layer_spacing for i in range(len(bottom_layers))]

    for y, num_bars in zip(y_bottom_layers, bottom_layers):
        x_positions = calculate_rebar_positions(c, b, num_bars, main_dia, travesre_dia)
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

    # Calculate positions of top reinforcement layers
    y_top_layers = [d - c - (i + 0.5) * layer_spacing for i in range(len(top_layers))]

    for y, num_bars in zip(y_top_layers, top_layers):
        x_positions = calculate_rebar_positions(c, b, num_bars, main_dia, travesre_dia)
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
    if no_of_middle_rebars > 0:
        n = int(no_of_middle_rebars // 2)
        d_middle = min(y_top_layers) - max(y_bottom_layers)
        s = d_middle / (n + 1)

        for i in range(1, n + 1):
            y_position = max(y_bottom_layers) + s * i
            fig.add_shape(
                type="circle",
                x0=c + travesre_dia,
                y0=y_position - middle_dia / 2,
                x1=c + travesre_dia + middle_dia,
                y1=y_position + middle_dia / 2,
                line=dict(color="blue"),
                fillcolor="blue",
            )
            fig.add_shape(
                type="circle",
                x0=b - c - travesre_dia - middle_dia,
                y0=y_position - middle_dia / 2,
                x1=b - c - travesre_dia,
                y1=y_position + middle_dia / 2,
                line=dict(color="blue"),
                fillcolor="blue",
            )

    # Set axis properties to ensure equal scale
    fig.update_xaxes(range=[-5, b + 5], scaleratio=1, zeroline=False)
    fig.update_yaxes(range=[-5, d + 5], scaleratio=1, zeroline=False)
    fig.update_layout(
        title=legend,
        xaxis_title="Width (cm)",
        yaxis_title="Depth (cm)",
        height=600,
        width=600,
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )

    # fig.show()
    return fig


def multi_sections(
    N,
    b,
    h,
    covering,
    main_dia,
    traverse_dia,
    middle_dia,
    bottom_layers,
    top_layers,
    no_of_middle_rebars,
    legend,
):
    sections_fig = []
    for i in range(N):
        figure = go.Figure()

        fig = section_fig(
            figure,
            b,
            h,
            covering,
            main_dia[i],
            traverse_dia[i],
            middle_dia[i],
            bottom_layers[i],
            top_layers[i],
            no_of_middle_rebars[i],
            legend[i],
        )
        sections_fig.append(fig)

    return sections_fig


def create_html(sfd_bmd_fig, sections_fig):
    if sfd_bmd_fig is not None:
        sfd_bmd_html = sfd_bmd_fig.to_html(full_html=False, include_plotlyjs="cdn")
    else:
        sfd_bmd_html = "Hello World!"

    # Start building the HTML content
    html_content = f"""
    <html>
        <head>
            <title>Sections</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1>SFD, BMD</h1>
            <div class="plot-curve">{sfd_bmd_html}</div>
            <h1>Sections</h1>
    """

    # Loop through the list of figures, displaying 4 per row
    for i in range(len(sections_fig)):
        if i % 4 == 0:  # Start a new row every 4 sections
            if i != 0:  # Close the previous row div if it's not the first
                html_content += "</div>"
            html_content += """<div class="plot-sections" style="display: flex; justify-content: space-around; margin-bottom: 30px;">"""

        # Convert each figure to HTML
        section_html = sections_fig[i].to_html(full_html=False, include_plotlyjs=False)

        # Add the section plot to the current row
        html_content += f"""
            <div style="width: 23%;">
                <h2>Section Plot {i + 1}</h2>
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
