import streamlit as st
import base64
import pathlib
import os


def render_svg(svg:str) -> None:
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

# Set up the Streamlit page
st.set_page_config(
    layout="wide",
    page_title="Story - Pinkbombs",
    page_icon="🍣",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
    body {
    background-image: url("http://localhost:8501/app/static/page_1.png");
    background-size: cover;
    }
</style>
""",
    unsafe_allow_html=True,
)


header_col = st.columns((0.1, 0.3, 1, 0.1, 0.1))
with header_col[0]:
    st.title("Pinkbombs (placeholder)")
with header_col[3]:
    if st.button("Story"):
        st.switch_page("main.py")
with header_col[4]:
    if st.button("Data"):
        st.switch_page("pages/1_data.py")
# # Create a container to hold the images
# image_container = st.container()

st.image("http://localhost:8501/app/static/pages/page_1.png", use_column_width=True)
st.image("http://localhost:8501/app/static/pages/page_2.png", use_column_width=True)
st.image("http://localhost:8501/app/static/pages/page_3.png", use_column_width=True)
st.image("http://localhost:8501/app/static/pages/page_4.png", use_column_width=True)
st.image("http://localhost:8501/app/static/pages/page_5.png", use_column_width=True)
st.image("http://localhost:8501/app/static/pages/page_6.png", use_column_width=True)
st.image("http://localhost:8501/app/static/pages/page_7.png", use_column_width=True)
st.image("http://localhost:8501/app/static/pages/page_8.png", use_column_width=True)
st.image("http://localhost:8501/app/static/pages/page_9.png", use_column_width=True)
st.image("http://localhost:8501/app/static/pages/footer.png", use_column_width=True)

# # Add some content below the images
