import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure


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
    input_df, input_x, input_y, title, palette=px.colors.qualitative.Pastel1, theme="simple_white"
) -> Figure:
    """Returns plotly express object as area chart with a single line
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualised
            input_x (str): name of the field for the x axis
            input_y (str): name of the field for the y axis
            title (str): chart title
            palette (px.object): plotly discrete palette, default is Pastel1
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            area (plotly object): output chart object
    """
    area = px.area(
        input_df,
        x=input_x,
        y=input_y,
        color_discrete_sequence=palette,
    )
    area.update_layout(template=theme, title=title)
    area.update_yaxes(exponentformat="none")
    return area


def make_area_order_chart(
    input_df,
    input_x,
    input_y,
    input_col,
    title,
    reorder=False,
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
            reorder (boolean): if true, dataframe is reodered by the input_col field, defauls is False
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
    area.update_layout(template=theme, title=title)
    area.update_yaxes(exponentformat="none")

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

    return area


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
    theme="simple_white",
) -> Figure:
    """Returns plotly express object as bar chart
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
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            bar (plotly object): output chart object
    """
    # Sort out number format
    input_df[input_x] = input_df[input_x].str.replace(",", ".")
    input_df[input_x] = input_df[input_x].astype(float)

    # Recalculate %
    input_df[input_col] = input_df[input_x] / input_df[input_x].sum()

    # Concatenate input_y1 and input_y2 to form input_y
    input_y = input_y1 + "_" + input_y2
    input_df[input_y] = input_df[input_y1] + " " + input_df[input_y2]

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
        hover_data={input_x: ":,.0f", input_y: False, input_col: ":.1%"},
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
    )
    bar.update_xaxes(exponentformat="none", range=[0, 2000000])
    bar.update_yaxes(ticks="")
    bar.update_coloraxes(colorbar_tickformat="0%")

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
    Returns:
            bar (Plotly object): output chart object
    """
    # Reorder the dataframe
    input_df = input_df.sort_values(input_x, ascending=False)

    # Concatenate input_y1 and input_y2 to form input_y
    input_y = input_y1 + "_" + input_y2
    input_df[input_y] = input_df[input_y1] + " " + input_df[input_y2]

    # Replace NaN values with an empty string in all columns
    input_df = input_df.fillna("")

    # Get a list of all columns except input_x, input_y1, and input_y2
    hover_data = {input_x: ":,.0f", input_y: False}
    for column in input_other:
        hover_data[column] = True

    # Remove '~' characters from input_n1 and input_n2 and convert them to integers
    input_df[input_n1] = input_df[input_n1].str.replace("~", "")
    input_df[input_n2] = input_df[input_n2].str.replace("~", "")
    input_df[input_n1] = input_df[input_n1].astype(int)
    input_df[input_n2] = input_df[input_n2].astype(int)

    # Divide the values in input_n1 by 1,000,000 to display revenues in millions
    input_df[input_n1] = input_df[input_n1] / 1_000_000
    # Format the values with "$" symbol preceding and add "M" for millions and "B" for billions
    input_df[input_n1] = input_df[input_n1].map(
        lambda x: f"${x:.1f}M" if x < 1000 else f"${x/1000:.1f}B"
    )

    # Format the values in input_n2 with commas for thousand separators
    input_df[input_n2] = input_df[input_n2].apply(lambda x: f"{x:,.0f}")

    # Loop through the DataFrame and update values for the company "Cooke"
    for index, row in input_df.iterrows():
        if row[input_y1] == "Cooke":
            input_df.at[index, input_n2] = "~" + str(row[input_n2])
            input_df.at[index, input_n1] = "~" + str(row[input_n1])

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
    )
    bar.update_xaxes(exponentformat="none")
    bar.update_yaxes(ticks="")

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


def make_animated_bubble_map(
    input_df,
    input_loc,
    input_hover,
    input_time,
    input_size,
    title,
    size_max=50,
    palette=px.colors.qualitative.Prism,
    theme="simple_white",
) -> Figure:
    """Returns plotly express object as Bubbles map with animation
    Parameters:
            input_df (pd.DataFrame): dataframe with data to be visualised
            input_loc (str): name of the field with the iso alpha3 codes
            input_hover (str): name of the field to show on hover
            input_time (str): name of the time field for the animation
            input_size (str): name of the field for the size of the bubbles
            title (str): chart title
            size_max (int): size of the maximum bubble radius, default=50
            palette (px.object): plotly discrete palette, default is Prism
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            area (plotly object): output chart object
    """
    map = px.scatter_geo(
        input_df,
        locations=input_loc,
        size=input_size,
        animation_frame=input_time,
        projection="natural earth",
        size_max=size_max,
        hover_name=input_hover,
        hover_data={input_size: ":,.0f", input_time: True, input_hover: False, input_loc: False},
        color_discrete_sequence=palette,
        title=title,
    )
    return map
