import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pandas as pd


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


def get_rebar_coordinates(
    b, d, c, main_dia, travesre_dia, bottom_layers, top_layers, middle_rebars
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
                {"x": c + travesre_dia + main_dia / 2, "y": y_position, "z": z}
            )
            rebar_data.append(
                {"x": b - c - travesre_dia - main_dia / 2, "y": y_position, "z": z}
            )

    return pd.DataFrame(rebar_data)


def plot_rc_section(
    fig, b, d, c, travesre_dia, main_dia, bottom_layers, top_layers, middle_rebars
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
    if middle_rebars > 0:
        n = middle_rebars // 2
        d_middle = min(y_top_layers) - max(y_bottom_layers)
        s = d_middle / (n + 1)

        for i in range(1, n + 1):
            y_position = max(y_bottom_layers) + s * i
            fig.add_shape(
                type="circle",
                x0=c + travesre_dia,
                y0=y_position - main_dia / 2,
                x1=c + travesre_dia + main_dia,
                y1=y_position + main_dia / 2,
                line=dict(color="blue"),
                fillcolor="blue",
            )
            fig.add_shape(
                type="circle",
                x0=b - c - travesre_dia - main_dia,
                y0=y_position - main_dia / 2,
                x1=b - c - travesre_dia,
                y1=y_position + main_dia / 2,
                line=dict(color="blue"),
                fillcolor="blue",
            )

    # Set axis properties to ensure equal scale
    fig.update_xaxes(range=[-5, b + 5], scaleratio=1, zeroline=False)
    fig.update_yaxes(range=[-5, d + 5], scaleratio=1, zeroline=False)
    fig.update_layout(
        title="RC Beam/Column Section",
        xaxis_title="Width (cm)",
        yaxis_title="Depth (cm)",
        height=600,
        width=600,
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )

    # fig.show()
    return fig


def create_one_plot(
    b,
    h,
    covering,
    traverse_dia,
    main_dia,
    bottom_layers,
    top_layers,
    middle_rebars,
):
    section_fig = go.Figure()
    section_fig = plot_rc_section(
        section_fig,
        b,
        h,
        covering,
        traverse_dia / 10,
        main_dia / 10,
        bottom_layers,
        top_layers,
        middle_rebars,
    )

    return section_fig


def create_html(
    sfd_bmd_fig,
    N,
    b,
    h,
    covering,
    traverse_dia,
    main_dia,
    bottom_layers,
    top_layers,
    middle_rebars,
):
    section_htmls = []
    for i in range(N):
        section_fig = create_one_plot(
            b,
            h,
            covering,
            traverse_dia[i],
            main_dia[i],
            bottom_layers[i],
            top_layers[i],
            middle_rebars[i],
        )
        # Save each plot to a string
        section_html = section_fig.to_html(full_html=False, include_plotlyjs="cdn")
        section_htmls.append(section_html)

    if sfd_bmd_fig != None:
        sfd_bmd_html = sfd_bmd_fig.to_html(full_html=False, include_plotlyjs="cdn")
    else:
        sfd_bmd_html = "Hello World!"

    print(f"\nCongrate!! Open rectangle_plot.html and do not serious!")

    # Combine all plots into one HTML file
    with open("rectangle_plot.html", "w") as f:
        f.write(
            f"""
        <html>
            <head>
                <title>Rectangle Plot</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    .plot-container {{
                        display: flex;
                        flex-direction: row;
                        flex-wrap: wrap;
                        justify-content: space-around;
                    }}
                    .plot-item {{
                        flex: 0 0 auto;
                        margin: 10px;
                    }}
                </style>
            </head>
            <body>
                <h1>SFD, BMD</h1>
                <div class="plot-item">{sfd_bmd_html}</div>
                <h1>Section Plots</h1>
                <div class="plot-container">
                    {''.join([f'<div class="plot-item">{plot}</div>' for plot in section_htmls])}
                </div>
            </body>
        </html>
        """
        )
