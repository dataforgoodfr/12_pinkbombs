import matplotlib.pyplot as plt
import numpy as np

# Création de la liste des années : 
annees = np.arange(1950, 2021, 10)

def etat_pop_poissons():
    
    # Création listes : 
    sur_peche = []
    seuil_max = []
    sous_pêche = []
    
    # Complétion : 
    for y in annees: 
        data_1 = np.random.randint(0, 101)
        data_2 = np.random.randint(0, 101 - data_1)
        data_3 = 100 - data_1 - data_2
        
        sur_peche.append(data_1)
        seuil_max.append(data_2)
        sous_pêche.append(data_3)
    
    # Tracé du graphique :
    plt.figure(figsize=(8, 6))
    
    plt.stackplot(annees, sous_pêche, seuil_max, sur_peche, labels=['Sous-pêché', 'Seuil maximal', 'Sur-pêché'])

    plt.xlim(annees.min(), annees.max())
    plt.ylabel('%')
    plt.ylim(0,100)
    plt.legend(loc='upper left', bbox_to_anchor=[1, 1])
    plt.tight_layout()
    
    plt.show()

def conso_poissons():
    # Création des listes de données
    peche = [20]
    aquaculture = [20]

    # Complétion des données
    for y in range(len(list(annees)) - 1):
        elt_peche = peche[-1] + np.random.randint(-5, 10)
        peche.append(elt_peche)
        elt_aquaculture = aquaculture[-1] + np.random.randint(-5, 20)
        aquaculture.append(elt_aquaculture)

    # Tracé du graphique
    plt.figure(figsize=(8, 6))

    # Courbes pleines pour la pêche et l'aquaculture
    plt.fill_between(annees, peche, color='blue', alpha=0.3, label='Pêche')
    plt.fill_between(annees, aquaculture, color='green', alpha=0.3, label='Aquaculture')

    plt.xlim(annees.min(), annees.max())
    plt.ylim(0, None)
    plt.ylabel('Million de tonnes')
    plt.legend(loc='upper left', bbox_to_anchor=[1, 1])
    plt.tight_layout()
    plt.show()
    
def conso_par_hab():
    
    # Création des listes de données
    conso = [10]
    
    # Complétion des données
    for y in range(len(list(annees)) - 1):
        elt = conso[-1] + np.random.randint(-1, 10)
        conso.append(np.random.randint(10, 50))
    

     # Tracé du graphique
    plt.figure(figsize=(8, 6))

    # Courbes pleines pour la pêche et l'aquaculture
    plt.fill_between(annees, conso, color='blue', alpha=0.3, label='Commation par \nhabitant')

    plt.xlim(annees.min(), annees.max())
    plt.ylim(0, None)
    plt.ylabel('Kg/an')
    plt.legend(loc='upper left', bbox_to_anchor=[1, 1])
    plt.tight_layout()
    plt.show()
        


