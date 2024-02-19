####################################################################################
# API - Interface Pages 2 - 'Les chiffres'
####################################################################################

####################################################################################
# Importaion des librairies 

import streamlit as st 
from datetime import date
from modules import graphe

####################################################################################
# Variables à récupérer : 
date_maj = date.today()
data1 = 1500
data2 = "{:,}".format(13000000).replace(',', ' ')
data3 = 11.1 
data4 = 120

####################################################################################
# Container 1 :  

def container_1():
    """
    Affichage du container 'EN un coup d'oeil'. 
    """
    
    # Affichage du titre et de la date de MAJ  : 
    st.title("En un coup d'oeil")
    st.caption(f"Mise à jour : {date_maj}")

    # Création des marges et colonnes d'affichage : 
    marge_1, col1, col2, col3, col4, marge_2 = st.columns([0.25 , 1, 1, 1, 1, 0.25])
    
    # Colonne 1 : 
    with col1:
        st.markdown(
            f"""
            ## {data1} \n
            Saumons consommés depuis que vous êtes sur le site internet
            """
            )
        
    # Colonne 2 : 
    with col2:
        st.markdown(
            f"""
            ## {data2} \n
            Saumons consommés en France cette année
            """
            )
        
    # Colonne 3 : 
    with col3: 
        st.markdown(
            f"""
            ## {data3}% \n
            Croissance de la consomation de saumons dans le monde depuis 10 ans
            """
            )
    
    # Colonne 4 :         
    with col4: 
        st.markdown(
            f"""
            ## {data4} Gt eCO2 \n
            Impact carbonne de l'industrie du saumon sur l'année passée
            """
            )
    
def container_2():
    """
    Afiichage container 2, graphes 'Etat des populations de poissons' et 'Consommation de poissons'
    """
    
    # Création des marges et colonnes d'affichage :         
    marge_1, col1, marge_2, col2, marge_3 = st.columns([0.15 , 1, 0.10,  1, 0.15])
        
    # Graphe 1 : 
    with col1:
        
        # Création colonnes intermédiaries : 
        col1_bis, col2_bis = st.columns([5, 1])
        
        # Titre graphe : 
        col1_bis.markdown("### Etat des populations de poissons")
        
        # Menu Déroulant :
        option_graphe_1 = col2_bis.selectbox('',['Option 1', 'Option 2', 'Option 3'], key='menu_grpahe_1', index=None, placeholder="Plus") 

        # Explications : 
        st.markdown("""
                    On prélève en moyenne
                    <span style="font-size:30px; font-weight:bold;">4 436 cas</span> 
                    positifs au Covid19 chaque jour, 
                    <span style="background-color: lightgreen;">en baisse (- 32 %)</span>
                    par rapport à la semaine dernière (par date de prélèvement,j-3.
                    """, 
                    unsafe_allow_html=True,
                    )
        
        # Affichage du graphique : 
        st.pyplot(graphe.etat_pop_poissons())
    
    # Graphe 2 : 
    with col2: 
        
        # Création colonnes intermédiaries : 
        col1_bis, col2_bis = st.columns([5,1])
         
        # Titre graphe : 
        col1_bis.markdown("### Consommation de poissons")
        
        # Menu Déroulant :
        option_graphe_2 = col2_bis.selectbox('',['Option 1', 'Option 2', 'Option 3'], key='menu_grpahe_2', index=None, placeholder="Plus") 

        # Explications : 
        st.markdown("""
                    Il y a en moyenne
                    <span style="font-size:30px; font-weight:bold;">31 admissions</span>
                    pour Covid19 chaque jour, 
                    <span style="background-color: lightgreen;">en baisse (- 20 %)</span>
                    par rapport à la semaine dernière.
                    """, 
                    unsafe_allow_html=True,
                    )
        
        # Affichage graphe : 
        st.pyplot(graphe.conso_poissons())

def container_3():
    """
    Afiichage container 2, un seul graphe 'consommation de saumons par habitant/an'
    """
    
    # Création des marges et colonnes d'affichage :         
    marge_1, col1, marge_3 = st.columns([0.7, 1, 0.7])
    
    with col1: 
         # Titre graphe : 
        st.markdown("### Consommation de saumon par habitant et par an")
        
        # Explication : 
        st.markdown(
            """
            Eplication à mettre. 
            """
            )
        
        # Affichage graphe : 
        st.pyplot(graphe.conso_par_hab())
        
        
        
0,4166
  
         
        
        
        
    
    
    
