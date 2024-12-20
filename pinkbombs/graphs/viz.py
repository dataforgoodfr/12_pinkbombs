import pandas as pd
import numpy as np
import plotly.express as px
from plotly.graph_objects import Figure, Scatter, Heatmap
import textwrap
from plotly.subplots import make_subplots


def make_area_chart(input_df: pd.DataFrame, input_x: str, input_y: str) -> Figure:
    group_df = input_df[[input_x, input_y]].groupby(input_x).sum().reset_index()
    group_df = group_df.sort_values(by=input_y, ascending=False).iloc[:5]
    area = px.area(
        input_df,
        x="Year",
        y=input_y,
        color=input_x,
        line_group=input_x,
    )
    return area


def make_area_single_chart(
    input_df,
    input_x,
    input_y,
    title,
    palette=px.colors.qualitative.Pastel1,
    theme="simple_white",
    source_text="",
    block_zoom=False,
) -> Figure:
    """Returns plotly express object as area chart with a single line
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualised
            input_x (str): name of the field for the x axis
            input_y (str): name of the field for the y axis
            title (str): chart title
            palette (px.object): plotly discrete palette, default is Pastel1
            theme (str): plotly chart theme, default is 'simple_white'
            source_text (string): Text to display as source at the bottom. Default is empty.
            block_zoom (boolean): Decide if plotly should block the zoom. Default is False.
    Returns:
            area (plotly object): output chart object
    """
    area = px.area(
        input_df,
        x=input_x,
        y=input_y,
        color_discrete_sequence=palette,
    )
    area.update_layout(template=theme, title=title, hoverlabel=dict(bgcolor="white"))
    area.update_yaxes(exponentformat="none")
    area.update_xaxes(title=None)

    if source_text != "":
        area.update_layout(margin=dict(l=50, r=50, t=60, b=80))
        area.update_layout(
            annotations=[
                dict(
                    text=source_text,
                    font=dict(size=12),
                    showarrow=False,
                    xref="paper",
                    x=0,
                    yref="paper",
                    y=-0.15,
                )
            ]
        )

    if block_zoom:
        area.layout.xaxis.fixedrange = True
        area.layout.yaxis.fixedrange = True

    return area


def make_area_order_chart_grouped(
    input_df,
    input_x,
    input_y,
    title,
    color="#fd442f",
    theme="simple_white",
) -> Figure:
    """Returns plotly express object as area chart with multiple lines
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualised
            input_x (str): name of the field for the x axis
            input_y (str): name of the field for the y axis
            input_col (str): name of the field for the colors
            title (str): chart title
            reorder (boolean): if true, dataframe is reodered by the input_col field, 
                default is False
            palette (px.object): plotly discrete palette, default is Dark24
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            area (plotly object): output chart object
    """
    # Data cleaning
    try:
        input_df[input_y] = input_df[input_y].str.replace(",", ".")
        input_df[input_y] = input_df[input_y].astype(float)
    except Exception as e:
        print("Input is not in string format")

    input_df = input_df.groupby(input_x)[input_y].sum().reset_index()
    input_df["color"] = color

    area = Figure()
    area.add_trace(
        Scatter(
            x=input_df[input_x],
            y=input_df[input_y],
            fill="tozeroy",
            line=dict(color=color),
            mode="lines",
        )
    )
    area.update_layout(template=theme, title=title, xaxis_title=input_x, yaxis_title=input_y)
    area.update_yaxes(exponentformat="none", showgrid=True)

    return area


def make_area_order_chart(
    input_df,
    input_x,
    input_y,
    input_col,
    title,
    y_title,
    min_date,
    reorder=False,
    hide_zoom=False,
    palette=px.colors.qualitative.Dark24,
    theme="simple_white",
) -> Figure:
    """Returns plotly express object as area chart with multiple lines
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualised
            input_x (str): name of the field for the x axis
            input_y (str): name of the field for the y axis
            input_col (str): name of the field for the colors
            title (str): chart title
            y_title (str): y axis title
            min_date (int): minimum year to be shown on plot initially
            reorder (boolean): if true, dataframe is reodered by the input_col field, 
                default is False
            hide_zoom (boolean): to hide the zoom in top right corner
            palette (px.object): plotly discrete palette, default is Dark24
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            area (plotly object): output chart object
    """
    # Data cleaning - TO REMOVE
    input_df[input_y] = input_df[input_y].str.replace(",", ".")
    input_df[input_y] = input_df[input_y].astype(float)

    if reorder:
        input_df_agg = input_df.groupby(input_col)[input_y].sum().sort_values(ascending=False)
        myorder = input_df_agg.reset_index()[input_col].tolist()
        input_df_u = input_df.set_index(input_col)
        input_df = input_df_u.loc[myorder].reset_index()

    area = px.area(
        input_df,
        x=input_x,
        y=input_y,
        color=input_col,
        color_discrete_sequence=palette,
    )
    area.update_layout(template=theme, title=title, yaxis_title=y_title)
    area.update_yaxes(exponentformat="none")
    area.update_xaxes(title=None, range=[min_date, input_df[input_x].max()])

    # Ability to select/deselect all
    area.update_layout(
        dict(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    buttons=list(
                        [
                            dict(
                                args=["visible", "legendonly"],
                                label="Deselect All",
                                method="restyle",
                            ),
                            dict(args=["visible", True], label="Select All", method="restyle"),
                        ]
                    ),
                    pad={"r": 10, "t": 10},
                    showactive=False,
                    x=1,
                    xanchor="right",
                    y=1.1,
                    yanchor="top",
                ),
            ]
        )
    )

    # Remove zoom
    if hide_zoom:
        area.update_layout(modebar_remove=["zoom", "zoomIn", "zoomOut"])

    return area


def make_area_chart_options(
    input_df,
    input_x,
    input_y,
    title,
    legend_title,
    color_area="#fd442f",
    color_axis="white",
    theme="simple_white",
) -> Figure:
    """Returns plotly express object as area chart with single lines
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualised
            input_x (str): name of the field for the x axis
            input_y (str): name of the field for the y axis
            title (str): chart title
            legend_title (str): legend title
            color_area (str): color for the single area
            color_axis (str): color of the axis, lines and font over transparent background, 
                default is white
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            area (plotly object): output chart object
    """
    # Data cleaning
    try:
        input_df[input_y] = input_df[input_y].str.replace(",", ".")
        input_df[input_y] = input_df[input_y].astype(float)
    except Exception as e:
        print("Input is not in string format")

    fig = px.area(
        input_df,
        x=input_x,
        y=input_y,
        color_discrete_sequence=[color_area],
        line_shape="spline",
    )

    fig.update_layout(template=theme, title=title, yaxis_title=None, xaxis_title=None)

    fig.update_yaxes(
        exponentformat="none",
        tickformat="~s",
        # showgrid=True,
        color=color_axis,
        linecolor=color_axis,
    )
    fig.update_xaxes(color=color_axis, linecolor=color_axis)

    # Remove hover functionality
    fig.update_traces(hovertemplate=None, hoverinfo="skip")

    # Set area with single color
    fig.for_each_trace(lambda trace: trace.update(fillcolor=trace.line.color))

    # Set up legend
    fig.update_traces(showlegend=True)
    fig.for_each_trace(lambda trace: trace.update(name=legend_title))
    fig.update_layout(legend=dict(yanchor="top", y=1, xanchor="left", x=0.01))

    # Block zoom
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    # Set background to transparent and axes in white
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        },
        font_color=color_axis,
    )
    fig.layout.yaxis.color = color_axis
    fig.layout.legend.font.color = color_axis
    # fig.layout.yaxis.gridcolor = color_axis

    return fig


def make_color_bar_chart(
    input_df,
    input_x,
    input_y1,
    input_y2,
    input_col,
    title,
    xtitle,
    ytitle,
    palette=px.colors.sequential.Burg,
    block_zoom=False,
    theme="simple_white",
) -> Figure:
    """Returns plotly express object as bar chart - specific to graph 1.3 ATM!!!
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualised
            input_x (str): name of the field for the x axis
            input_y1 (str): name of the first part of the field for the y axis
            input_y2 (str): name of the second part of the field for the y axis
            input_col (str): name of the field to display in color
            title (str): chart title
            xtitle (str): x-axis title
            ytitle (str): y-axis title
            palette (px.object): plotly discrete palette, default is Burg
            block_zoom (boolean): Decide if plotly should block the zoom. Default is False.
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            bar (plotly object): output chart object
    """
    # Sort out number format
    try:
        input_df[input_x] = input_df[input_x].str.replace(",", ".")
        input_df[input_x] = input_df[input_x].astype(float)
    except Exception as e:
        print("Input is not in string format")

    # Recalculate %
    input_df[input_col] = input_df[input_x] / input_df[input_x].sum()

    # Concatenate input_y1 and input_y2 to form input_y
    input_y = input_y1 + "_" + input_y2
    input_df[input_y] = input_df[input_y1] + " " + input_df[input_y2]

    # Make figures in tonnes priettier
    input_df['Production'] = input_df[input_x].apply(lambda x: f"{x:,.0f}") + str(" tonnes")

    bar = px.bar(
        input_df,
        y=input_y,
        x=input_x,
        color=input_col,
        orientation="h",
        category_orders={input_y: input_df[input_y].tolist()},
        text_auto=",.0f",
        title=title,
        color_continuous_scale=palette,
        hover_name=input_y,
        hover_data={input_x: False, input_y: False, 'Production': True, input_col: ":.1%"},
    )

    bar.update_traces(
        textfont_size=12,
        textangle=0,
        textposition="outside",
        cliponaxis=False,
    )
    bar.update_layout(
        template="simple_white",
        xaxis_title=xtitle,
        yaxis_title=ytitle,
        yaxis=dict(tickfont=dict(size=13)),
        hoverlabel=dict(bgcolor="white"),
    )
    bar.update_xaxes(exponentformat="none", range=[0, 2000000])
    bar.update_yaxes(ticks="")
    bar.update_coloraxes(colorbar_tickformat="0%")

    if block_zoom:
        bar.layout.xaxis.fixedrange = True
        bar.layout.yaxis.fixedrange = True
        bar.update_layout(modebar_remove=["zoom", "pan", "lasso2d", "select2d"])

    return bar


def make_color_bar_chart2(
    input_df,
    input_x,
    input_y,
    input_col,
    col_rename,
    title,
    ytitle,
    palette=px.colors.qualitative.Pastel1,
    theme="simple_white",
) -> Figure:
    """Returns plotly express object as bar chart with gradient color - speficif to graph 4.2 ATM!!!
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualised
            input_x (str): name of the field for the x axis
            input_y (str): name of the field for the y axis
            input_col (str): name of the field to display in color
            col_rename (dict): dictionary with the column rename of input_df
            title (str): chart title
            ytitle (str): y-axis title
            palette (px.object): plotly discrete palette, default is Burg
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            bar (plotly object): output chart object
    """
    # Sort out number format
    input_df[input_y] = input_df[input_y].str.replace(",", ".")
    input_df[input_y] = input_df[input_y].astype(float)

    # Rename columns
    input_df = input_df.rename(columns=col_rename)

    bar = px.bar(
        input_df,
        y=col_rename[input_y],
        x=input_x,
        color=col_rename[input_col],
        title=title,
        color_continuous_scale=palette,
        hover_name=input_x,
        hover_data={col_rename[input_y]: ":,.0f", input_x: False, col_rename[input_col]: ":,.0f"},
    )
    bar.update_traces(
        textfont_size=12,
        textangle=0,
        textposition="outside",
        cliponaxis=False,
    )
    bar.update_layout(template="simple_white", yaxis_title=ytitle)
    bar.update_xaxes(exponentformat="none")

    return bar


def make_simple_bar_chart(
    input_df,
    input_x,
    input_y1,
    input_y2,
    input_n1,
    input_n2,
    input_other,
    title,
    xtitle,
    ytitle,
    mycolor,
    block_zoom=False,
    fix_approx=True,
    palette=px.colors.qualitative.Pastel1,
    theme="simple_white",
) -> Figure:
    """Returns a Plotly Express object as a bar chart with only 1 color
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualized
            input_x (str): name of the field for the x-axis
            input_y1 (str): name of the field for the first part of the y-axis
            input_y2 (str): name of the field for the second part of the y-axis
            input_n1 (str): name of field for revenues in $
            input_n2 (str): name of field for employees
            input_other (List[str]): names of other fields to display on hover
            title (str): chart title
            xtitle (str): x-axis title
            ytitle (str): y-axis title
            mycolor (str): name of the color code for the bars
            palette (px.object): Plotly discrete palette, default is Pastel1
            theme (str): Plotly chart theme, default is 'simple_white'
            block_zoom (boolean): Decide if plotly should block the zoom. Default is False.
            fix_approx (boolean): if data has "~" symbol (to remove from this function!)
    Returns:
            bar (Plotly object): output chart object
    """
    # Reorder the dataframe
    input_df = input_df.sort_values(input_x, ascending=False)

    # Concatenate input_y1 and input_y2 to form input_y
    input_y = input_y1 + "_" + input_y2
    input_df[input_y] = input_df[input_y1] + " " + input_df[input_y2]

    if fix_approx:
        # Remove '~' characters from input_n1 and input_n2 and convert them to integers
        input_df[input_n1] = input_df[input_n1].str.replace("~", "")
        input_df[input_n2] = input_df[input_n2].str.replace("~", "")
        input_df[input_n1] = input_df[input_n1].astype(int)
        input_df[input_n2] = input_df[input_n2].astype(int)

    # Divide the values in input_n1 by 1,000,000 to display revenues in millions
    input_df[input_n1] = input_df[input_n1] / 1000000
    # Format the values with "$" symbol preceding and add "M" for millions and "B" for billions
    input_df[input_n1] = input_df[input_n1].map(
        lambda x: f"${x:.1f}M (2022)" if x < 1000 else f"${x/1000:.1f}B (2022)"
    )

    # Format the values in input_n2 with commas for thousand separators
    input_df[input_n2] = input_df[input_n2].apply(lambda x: f"{x:,.0f}") + str(" (2022)")

    # Loop through the DataFrame and update values for the company "Cooke"
    for index, row in input_df.iterrows():
        if row[input_y1] == "Cooke":
            input_df.at[index, input_n2] = "~" + str(row[input_n2])
            input_df.at[index, input_n1] = "~" + str(row[input_n1])

    # Replace NaN values with an empty string in all columns
    input_df = input_df.fillna("")

    # Make figures in tonnes priettier
    input_df['Production'] = input_df[input_x].apply(lambda x: f"{x:,.0f}") + str(" tonnes")

    # Replace revenues 2022 with revenues 
    input_df = input_df.rename(columns={input_n1:input_n1[:-5], input_n2: input_n2[:-5]})

    # Get a list of all columns except input_x, input_y1, and input_y2
    hover_data = {input_x: False, input_y: False, 'Production':True}
    for column in input_other:
        hover_data[column] = True

    bar = px.bar(
        input_df,
        y=input_y,
        x=input_x,
        orientation="h",
        category_orders={input_y: input_df[input_y].tolist()},
        text_auto=",.0f",
        title=title,
        color_discrete_sequence=palette,  # [px.colors.qualitative.Pastel1[0]],
        hover_name=input_y,
        hover_data=hover_data,
    )

    bar.update_traces(
        textfont_size=12, textangle=0, textposition="inside", cliponaxis=False, marker_color=mycolor
    )
    bar.update_layout(
        template="simple_white",
        xaxis_title=xtitle,
        yaxis_title=ytitle,
        yaxis=dict(tickfont=dict(size=13)),
        hoverlabel=dict(bgcolor="white"),
    )
    bar.update_xaxes(exponentformat="none")
    bar.update_yaxes(ticks="")

    if block_zoom:
        bar.layout.xaxis.fixedrange = True
        bar.layout.yaxis.fixedrange = True
        bar.update_layout(modebar_remove=["zoom", "pan", "lasso2d", "select2d"])

    return bar


def make_bar_chart(
    input_df,
    input_x,
    input_y,
    input_other,
    title,
    xtitle,
    palette=px.colors.qualitative.Pastel1,
    theme="simple_white",
) -> Figure:
    """Returns plotly express object as bar chart with only 1 color
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualised
            input_x (str): name of the field for the x axis
            input_y (str): name of the field for the y axis
            input_other (str): name of other field to display on hover
            title (str): chart title
            xtitle (str): x-axis title
            palette (px.object): plotly discrete palette, default is Pastel1
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            bar (plotly object): output chart object
    """
    # Reorder dataframe
    input_df = input_df.sort_values(input_x, ascending=False)

    bar = px.bar(
        input_df,
        y=input_y,
        x=input_x,
        orientation="h",
        category_orders={input_y: input_df[input_y].to_list()},
        text_auto=",.0f",
        title=title,
        color_discrete_sequence=palette,
        hover_name=input_y,
        hover_data={input_x: ":,.0f", input_y: False, input_other: True},
    )
    bar.update_traces(
        textfont_size=12,
        textangle=0,
        textposition="outside",
        cliponaxis=False,
    )
    bar.update_layout(template="simple_white", xaxis_title=xtitle)
    bar.update_xaxes(exponentformat="none")
    bar.update_coloraxes(colorbar_tickformat="0%")

    return bar


def make_treemap_chart(
    input_df, input_x1, input_x2, input_x3, input_y, input_n, title, height=400, width=500, top_x=6
) -> Figure:
    """Returns a Plotly Express object as a treemap chart
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualized
            input_x1 (str): name of the main field to build the treemap
            input_x2 (str): name of the field to calculate ratio
            input_x3 (str): name of the field for the %
            input_y (str): name of the field for the production
            input_n (str): name of field names
            height (int): number of pixels for chart height, default is 400
            width (int): number of pixels for chart width, default is 500
            top_x(int): top x to be shown in the treemap, default is 6
            title (str): title at top of the treemap
    Returns:
            fig (Plotly object): output treemap chart object
    """
    # Aggregate de dataframe, showing only the top x
    input_df_top = input_df.sort_values(input_x1, ascending=False).head(top_x)
    input_df_bot = input_df.sort_values(input_x1, ascending=False).loc[top_x:,].sum().to_frame().T
    input_df_bot[input_n] = "Others"
    input_df_bot[input_x3] = (input_df_bot[input_x1] / input_df_bot[input_x2]).apply(
        lambda x: f"{x:.2%}"
    )
    input_df_new = pd.concat([input_df_top, input_df_bot]).reset_index()

    # make Labels
    input_df_new["labels"] = input_df_new[input_n] + " - Escape rate = " + input_df_new[input_x3]

    # Treemap
    fig = px.treemap(
        input_df_new,
        path=[px.Constant(title), "labels"],
        values=input_x1,
        names="labels",
        width=width,
        height=height,
        color_discrete_sequence=[
            "#151c97",  # seastemik dark blue
            "#f4e8d7",  # seastemik terre
            "#e8ef50",  # seastemik positif
            "#f1461f",  # seastemik rouge
            "#eb88dd",  # seastemik rose
            "#7049ff",  # seastemik violet
            "#b1e848",  # seastemik vert clair
        ],
        hover_name="labels",
        hover_data={
            input_x1: ":,.0f",
            input_n: False,
            input_y: ":,.0f",
            "labels": False,
            input_x3: True,
        },
    )

    fig.update_traces(root_color="lightgrey")
    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            + "Number of escapes=%{value}<br>"
            + "Production (tonnes)=%{customdata[2]:,}<extra></extra>"
        )
    )
    fig.update_traces(textfont_size=14, selector=dict(type="treemap"))
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25), showlegend=True)

    return fig


def make_simple_pie_chart(
    input_df,
    names,
    values,
    title,
    hover_data,
    color_discrete_sequence,
    total_annotation=None,
    total_value=None,
    total_text="",
    textfont_size=16,
) -> Figure:
    """Returns a Plotly Express object as a pie chart
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualized
            names (str): name of the field for the names in the pie chart
            values (str): name of the field for the values in the pie chart
            title (str): chart title
            hover_data (dict): dictionary of columns to be included in the hover tooltip
            color_discrete_sequence (list): list of colors for the pie chart
            total_annotation (dict): annotation details for the total value (default=None)
            total_value (float): total value for annotation (default=None)
            total_text (str): text for total value (default='')
            textfont_size (int): font size for text (default=16)
    Returns:
            pie (Plotly object): output chart object
    """
    # Calculate percentages relative to the total
    input_df[values] = input_df[values].str.replace(",", ".").astype(float)
    total_sum = input_df[values].sum()
    input_df["Percentage"] = round(input_df[values] / total_sum * 100, 2)

    # Create the pie chart
    pie = px.pie(
        input_df,
        names=names,
        # values=values,
        values="Percentage",
        title=title,
        hover_data=hover_data,
        color_discrete_sequence=color_discrete_sequence,
        # custom_data=['Percentage']
    )

    # Add total annotation if provided
    pie.add_annotation(
        x=0,
        y=0,
        text=f"Total: {total_sum / 1_000_000:.2f} Millions tons of CO2 emitted",
        showarrow=False,
        font=dict(size=30),
    )
    # Update trace properties
    pie.update_traces(marker=dict(line=dict(color="#ffffff", width=2)), textfont_size=textfont_size)

    return pie


def make_simple_box_chart(
    input_df,
    input_x,
    input_y,
    title,
    xtitle,
    ytitle,
    block_zoom=False,
    palette=px.colors.qualitative.Pastel1,
    theme="simple_white",
) -> Figure:
    """Returns a Plotly Express object as a box plot with only 1 color
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualized
            input_x (str): name of the field for the x-axis
            input_y (str): name of the field for the y-axis
            title (str): chart title
            xtitle (str): x-axis title
            ytitle (str): y-axis title
            block_zoom (boolean): Decide if plotly should block the zoom. Default is False.
            palette (px.object): Plotly discrete palette, default is Pastel1
            theme (str): Plotly chart theme, default is 'simple_white'
    Returns:
            box (Plotly object): output chart object
    """
    # Reorder the dataframe
    input_df = input_df.sort_values(input_x, ascending=False)

    # Transform the input_y data
    try:
        input_df[input_y] = input_df[input_y].str.replace(",", ".")
        input_df[input_y] = input_df[input_y].astype(float)
    except Exception as e:
        print("Input is not in string format")

    # List of order and color
    my_order = input_df.groupby(input_x)[input_y].median().sort_values().index.tolist()
    my_col = ["#151c97"] * (len(my_order) - 1)
    my_col.append("#ff4530")

    # Create the box plot
    box = px.box(
        input_df,
        y=input_y,  # Use the input_y field for the y-axis
        x=input_x,
        color=input_x,
        title=title,
        category_orders={input_x: my_order},  # Update category orders accordingly
        color_discrete_sequence=my_col,
        hover_name=input_x,  # Update hover_name accordingly
    )

    box.update_layout(template=theme, yaxis_title=ytitle, showlegend=False)
    box.update_xaxes(exponentformat="none")
    box.update_coloraxes(colorbar_tickformat="0%")
    box.update_traces(boxpoints=False)  # remove outliers

    if xtitle is not None:
        box.update_layout(xaxis_title="<i>"+xtitle+"</i>", 
                          xaxis={'side': 'right'})
        box.update_xaxes(title_font_size=10)

    else:
        box.update_layout(xaxis_title=xtitle)

    # Remove hover
    box.update_traces(hovertemplate=None, hoverinfo="skip")

    if block_zoom:
        box.layout.xaxis.fixedrange = True
        box.layout.yaxis.fixedrange = True

    return box


def make_matrix_alternatives(
    input_df, max_len=60, max_len_col=11, width=900, height=500, 
    legend_green="", legend_red="", hover_disable=False
) -> Figure:
    """Returns a Plotly Express object as a Heatmap for the matrix of altenatives
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualized
            title (str): chart title
            max_len (int): Number of characters for text wrapping, Default is 60.
            max_len_col (int): Number of characters for wrapping of columns names, Default is 11.
            width (int): Dimension of the figure, Default is 900.
            height (int): Dimension of the figure, Default is 500.
            legend_green (str): Text to display next to the green in the legend.
            legend_red (str): Text to display next to the red in the legend.
            hover_disable (boolean): Decide if disable the hover. Default is False.
    Returns:
            box (Plotly object): output chart object
    """

    # Extract columns and rows names from the dataframe
    col = input_df.columns.values.tolist()
    col.pop(0)
    row = input_df["Unnamed: 0"].tolist()[0:6]

    n_col = len(col)
    n_row = len(row)

    # Read the text into a matrix
    customdata = input_df[col].to_numpy()
    mat_col = input_df[col].to_numpy()

    for i in range(n_row):
        for j in range(n_col):
            pair = textwrap.fill(col[j] + " - " + row[i], max_len).replace("\n", "<br>")

            if j == 0:
                mat_col[i, j] = 7
                customdata[i, j] = f"<b>{row[i]}</b><br>" + \
                textwrap.fill(customdata[i, j], max_len).replace("\n", "<br>")
            else:
                mat_col[i, j] = int(customdata[i, j][0])  # Take color code
                customdata[i, j] = f"<b>{pair}</b><br>" + \
                textwrap.fill(customdata[i, j], max_len).replace("\n", "<br>")
    
    # Define colorscale and axes
    mycolorscale = [
        #"#bfcee1",  # light grey - NEW
        "#6ecb57",  # dark green - Paul
        "#aaed99",  # light green - Paul
        "#ffd336",  # yellow - Paul
        "#ffac3c",  # orange - Paul: #ff7e36. more yellow orange #ffac3c
        "#f34620",  # red - Paul
        "#cc0100",  # dark red - NEW
        "rgba(0,0,0,0)",  # transparent for the first column
    ]

    n=len(mycolorscale)
    my_colorsc=[[0, mycolorscale[0]],
            [1/n, mycolorscale[0]],
            [1/n, mycolorscale[1]],
            [2/n, mycolorscale[1]],
            [2/n, mycolorscale[2]],
            [3/n, mycolorscale[2]],
            [3/n, mycolorscale[3]],
            [4/n, mycolorscale[3]],
            [4/n, mycolorscale[4]],
            [5/n, mycolorscale[4]],
            [5/n, mycolorscale[5]],
            [6/n, mycolorscale[5]],
            [6/n, mycolorscale[6]],
            [1, mycolorscale[6]]]

    # Wrap column names
    if max_len_col is not None:
        col = [textwrap.fill(el, max_len_col).replace("\n", "<br>") for el in col]

    fig = Figure(
        Heatmap(
            x=col,
            y=row,
            z=mat_col,
            customdata=customdata,
            xgap=4,
            ygap=4,
            colorscale=my_colorsc,
            showscale=True,
            hovertemplate="%{customdata}<extra></extra>",
            hoverlabel=dict(bgcolor="white"),
        )
    )

    # Transparent background and x-axis on top
    fig.update_layout(
        yaxis_autorange="reversed",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
    )
    fig.update_xaxes(side="top")

    # Block zoom
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    if width is not None:
        fig.update_layout(width=width, height=height)

    if hover_disable:
        fig.update_traces(hovertemplate=None, hoverinfo="skip")

    tickvals = [1.4, 2.25, 3.1, 3.95, 4.8, 5.7]
    ticktext = [textwrap.fill(legend_green, 8).replace("\n", "<br>"), 
                "", "", "", "", 
                textwrap.fill(legend_red, 8).replace("\n", "<br>")]

    fig.update_traces(showscale=True, 
                      colorbar = dict(thickness=25, 
                                      tickvals=tickvals, 
                                      ticktext=ticktext))
    
    # Reduce range to see only a small section of the transparent cells (first col)
    fig.update_layout(xaxis_range=[0.3, 8.5])

    return fig

def make_double_yaxis_bar_chart(
    input_df,
    input_x1,
    input_x2,
    input_y1,
    input_y2,
    input_other,
    title,
    xtitle,
    ytitle1,
    ytitle2,
    mycolor_bar,
    bar_hover_legend,
    mycolor_point,
    point_hover_legend,
    block_zoom=False,
    theme="simple_white",
) -> Figure:
    """Returns a Plotly Express object as a bar chart with only 1 color
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualized
            input_x (str): name of the field for the x-axis
            input_y1 (str): name of the field for the first part of the y-axis
            input_y2 (str): name of the field for the second part of the y-axis
            input_n1 (str): name of field for revenues in $
            input_n2 (str): name of field for employees
            input_other (List[str]): names of other fields to display on hover
            title (str): chart title
            xtitle (str): x-axis title
            ytitle (str): y-axis title
            mycolor (str): name of the color code for the bars
            palette (px.object): Plotly discrete palette, default is Pastel1
            theme (str): Plotly chart theme, default is 'simple_white'
            block_zoom (boolean): Decide if plotly should block the zoom. Default is False.
            fix_approx (boolean): if data has "~" symbol (to remove from this function!)
    Returns:
            bar (Plotly object): output chart object
    """
    # Reorder the dataframe
    input_df = input_df.sort_values(input_y1, ascending=False)

    # Concatenate input_y1 and input_y2 to form input_y
    input_x = input_x1 + "_" + input_x2
    input_df[input_x] = input_df[input_x1] + " " + input_df[input_x2]

    input_df[input_y1] = np.round(input_df[input_y1], 0)
    input_df[input_y2] = np.round(input_df[input_y2], 2)
    input_df[input_other[0]] = np.round(input_df[input_other[0]], 0)
    input_df[input_other[1]] = np.round(input_df[input_other[1]], 0)
    input_df[input_other[2]] = np.round(input_df[input_other[2]], 0)

    input_df[input_other[0]] = input_df[input_other[0]].apply(lambda x: f"{x:,.0f}")
    input_df[input_other[1]] = input_df[input_other[1]].apply(lambda x: f"{x:,.0f}")
    input_df[input_other[2]] = input_df[input_other[2]].apply(lambda x: f"{x:,.0f}")
    # Get a list of all columns except input_x, input_y1, and input_y2
    hover_data = {input_x: False, input_y1: True, input_y2: True}
    for column in input_other:
        hover_data[column] = True

    # figure setup with multiple axes
    bar_point = make_subplots(specs=[[{"secondary_y": True}]])

    bar = px.bar(
        input_df,
        x=input_x,
        y=input_y1,
        orientation='v',
        category_orders={input_y1: input_df[input_y1].to_list()},
        text_auto=',.0f', # add
        # comma #'.2s' / '~s'
        title=title,
        hover_data=hover_data
        )

    bar.update_traces(marker_color=mycolor_bar,textfont_size=12, textangle=0, textposition="outside", cliponaxis=False,
                         hovertemplate = "<b>" + bar_hover_legend +': %{y} tonnes</b><br>'+
                                         "<i>- "+input_other[0] + ": %{customdata[1]} tonnes</i><br>"+
                                         "<i>- "+input_other[1] + ": %{customdata[2]} tonnes</i><br>" +
                                         "<i>- "+input_other[2] + ": %{customdata[3]} tonnes</i><br>")

    point = px.scatter(
        input_df,
        x=input_x,
        y=input_y2,
        hover_data={input_x: False, input_y1: False, input_y2: True}
        )

    point.update_traces(marker_color=mycolor_point, marker=dict(size=10),yaxis="y2",
                        hovertemplate = "<b>" + point_hover_legend +': %{y} kilos</b>')

    bar_point.add_traces(bar.data + point.data)

    bar_point.layout.xaxis.title = xtitle
    bar_point.layout.yaxis.title = ytitle1
    bar_point.layout.yaxis2.title = ytitle2
    bar_point.layout.yaxis2.color = mycolor_point

    # We adjust the zeros to start at the same level
    y1_min, y1_max = input_df[input_y1].min(), input_df[input_y1].max()
    y1_padding = (y1_max - y1_min) / 16
    y1_range = [y1_min - y1_padding, y1_max + y1_padding]
    y1_relative_zero = (0 - y1_range[0]) / (y1_range[1] - y1_range[0])

    y2_min, y2_max = input_df[input_y2].min(), input_df[input_y2].max()
    y2_padding = (y1_relative_zero * (y2_max - y2_min) + y2_min) / (1 - 2 * y1_relative_zero)
    y2_range = [y2_min - y2_padding, y2_max + y2_padding]

    bar_point.update_yaxes(range=y1_range, secondary_y=False)
    bar_point.update_yaxes(range=y2_range, secondary_y=True)
    bar_point.update_layout(template=theme,title=title,
        yaxis=dict(tickfont=dict(size=13)),
        hoverlabel=dict(bgcolor="white"))
    bar_point.update_xaxes(exponentformat="none")
    bar_point.update_coloraxes(colorbar_tickformat='0%')
    bar_point.update_layout(hovermode="x unified",xaxis_title=None)
    bar_point.update_xaxes(ticks="")

    if block_zoom:
        bar_point.layout.xaxis.fixedrange = True
        bar_point.layout.yaxis.fixedrange = True
        bar_point.layout.yaxis2.fixedrange = True
        bar_point.update_layout(modebar_remove=["zoom", "pan", "lasso2d", "select2d"])

    return bar_point