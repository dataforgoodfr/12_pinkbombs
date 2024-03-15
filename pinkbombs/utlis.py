import streamlit as st
from plotly.graph_objects import Figure


def make_double_pannel(
    chart_obj: Figure, text: str, switch: bool = False, chart_title: str = "",
) -> None:
    columns = st.columns((0.1, 0.5, 0.1, 0.6, 0.1), gap="medium")
    idx1 = 1 if switch else 3
    idx2 = 3 if switch else 1
    with columns[idx1]:
        if len(chart_title) > 0:
            st.markdown(
                f"<h4 style='text-align: center;'>{chart_title}</h4>", unsafe_allow_html=True,
            )
        st.plotly_chart(chart_obj, use_container_width=True)
    with columns[idx2]:
        st.markdown(
            """
        <style>
            [data-testid="column"] {
                display: flex;
                # flex-direction: column;
                align-items: center;
                justify-content: center;

            }
        </style>"""
            + f"<p style='text-align: center;'>{text}</p>",
            unsafe_allow_html=True,
        )
