import pandas as pd
import numpy as np
import plotly.express as px
from plotly.graph_objects import Figure, Scatter, Heatmap


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
            reorder (boolean): if true, dataframe is reodered by the input_col field, defauls is False
            palette (px.object): plotly discrete palette, default is Dark24
            theme (str): plotly chart theme, default is 'simple_white'
    Returns:
            area (plotly object): output chart object
    """
    # Data cleaning - TO REMOVE
    input_df[input_y] = input_df[input_y].str.replace(",", ".")
    input_df[input_y] = input_df[input_y].astype(float)

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


def make_color_bar_chart2(
    input_df,
    input_x,
    input_y,
    input_col,
    col_rename,
    title,
    ytitle,
    palette=px.colors.sequential.Burg,
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
            fix_approx (boolean): if data has "~" symbol (to remove from this function!)
    Returns:
            bar (Plotly object): output chart object
    """
    # Reorder the dataframe
    input_df = input_df.sort_values(input_x, ascending=False)

    # Concatenate input_y1 and input_y2 to form input_y
    input_y = input_y1 + "_" + input_y2
    input_df[input_y] = input_df[input_y1] + " " + input_df[input_y2]

    # Get a list of all columns except input_x, input_y1, and input_y2
    hover_data = {input_x: ":,.0f", input_y: False}
    for column in input_other:
        hover_data[column] = True

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
        lambda x: f"${x:.1f}M" if x < 1000 else f"${x/1000:.1f}B"
    )

    # Format the values in input_n2 with commas for thousand separators
    input_df[input_n2] = input_df[input_n2].apply(lambda x: f"{x:,.0f}")

    # Loop through the DataFrame and update values for the company "Cooke"
    for index, row in input_df.iterrows():
        if row[input_y1] == "Cooke":
            input_df.at[index, input_n2] = "~" + str(row[input_n2])
            input_df.at[index, input_n1] = "~" + str(row[input_n1])

    # Replace NaN values with an empty string in all columns
    input_df = input_df.fillna("")

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
    input_df = input_df.sort_values(by=input_time, ascending=False)
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
    map.update_geos(showcountries=True)

    return map


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
            palette (px.object): Plotly discrete palette, default is Pastel1
            theme (str): Plotly chart theme, default is 'simple_white'
    Returns:
            box (Plotly object): output chart object
    """
    # Reorder the dataframe
    input_df = input_df.sort_values(input_x, ascending=False)

    # Transform the input_y data
    input_df[input_y] = input_df[input_y].str.replace(",", ".")
    input_df[input_y] = input_df[input_y].astype(float)

    # Create the box plot
    box = px.box(
        input_df,
        y=input_y,  # Use the input_y field for the y-axis
        x=input_x,
        title=title,
        category_orders={
            input_x: input_df.groupby(input_x)[input_y].median().sort_values().index.tolist()
        },  # Update category orders accordingly
        color_discrete_sequence=palette,  # Set color palette
        hover_name=input_x,  # Update hover_name accordingly
    )

    box.update_layout(template=theme, xaxis_title=xtitle, yaxis_title="Mortality Rate (%)")
    box.update_xaxes(exponentformat="none")
    box.update_coloraxes(colorbar_tickformat="0%")

    return box


def make_matrix_alternatives(df_dummy, width=900, height=500, hover_disable=False):
    """Returns a waffle plot with 4 colors, with or without hover"""

    # Define size of matrix
    m = 5
    n = 8
    data = np.zeros((m, n))

    # Original data
    data_original = np.matrix([
            [2,2,3,2,0,0,0,0],
            [1,1,0,1,2,2,4,4],
            [0,0,1,1,1,1,4,1],
            [4,2,1,2,2,2,0,0],
            [4,3,2,2,0,0,0,0]])

    # Change data to have only one green   
    for i in range(m):
        for j in range(n):
            if data_original[i,j] == 0 or data_original[i,j] == 1:
                data[i,j] = 0
            else : 
                data[i,j] = data_original[i,j] - 1
    
    # Extra information to display on each cell
    extra_info = [['Extra information to provide on this cell' for c in range(n)] for r in range(m)]

    # Define colorscale and axes
    colorscale = [
                  #"#aaed99",  # light green
                  "#6ecb57",  # dark green
                  "#ffd336",  # yellow
                  "#ff7e36",  # orange
                  "#f34620"]  # red

    xlabels = ['Saumon<br>Elevage<br>terrestre',
              'Saumon<br>Elevage<br>en mer' ,
              'Pélagiques:<br>maquereaux/<br>sardines',
              "Mollusques &<br>Coquillages",
              "Algue", 'Graine de lin<br>ou noix', "Huile de<br>Colza",
              "Legumineuse<br>ou soja local"]
    ylabels = ['Metaux lourds', 'Apport en Omegas', 'Apport en proteines', 'Empreinte Carbone',
              'Impacts sociaux'] 

    fig = Figure(Heatmap(x=xlabels, y = ylabels, z=data,
                              customdata=extra_info, xgap=4, ygap=4,
                              colorscale=colorscale, 
                              showscale=False,
                              hovertemplate="(%{y}, %{x}): %{customdata}<extra></extra>"))
    fig.update_layout(width=width, height=height, 
                      yaxis_autorange='reversed',
                      paper_bgcolor="rgba(0,0,0,0)", 
                      plot_bgcolor="rgba(0,0,0,0)") #, template='simple_white')
    fig.update_xaxes(side='top') #visible=False, showticklabels=True)

    if hover_disable:
        fig.update_traces(hovertemplate = None, hoverinfo = "skip")

    return fig  

