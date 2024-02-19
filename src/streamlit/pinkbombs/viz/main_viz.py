####################################################################################
# Main Interface
###################################################################################

import streamlit as st
import page_2

####################################################################################
# Page Configuration 

st.set_page_config(
    page_title="pinkbombs",
    layout="wide", 
    initial_sidebar_state="auto",
    )

st.set_option('deprecation.showPyplotGlobalUse', False)

####################################################################################

# Banner for selecting pages: 
st.markdown("### Pinkbombs")
tab1, tab2  = st.columns([1, 1])

with tab1:
    tab1_selected = st.button("L'histoire")

with tab2:
    tab2_selected = st.button("Les chiffres")

# Page 2 - 'The Figures'
if tab2_selected:

    page_2.container_1() # Container 1
    st.divider() # Space

    page_2.container_2() # Container 2
    st.divider() # Space

    page_2.container_3() # Container
