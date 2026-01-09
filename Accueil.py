import streamlit as st


st.set_page_config(
    page_title="Accueil",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.title("⚡ Bilan énergétique – France métropolitaine")

st.markdown(
    """
### 🌍 Comprendre notre transition énergétique

**Quelle part de l’électricité que nous consommons provient d'énergies renouvelables ?**\n
**Les politiques publiques de transition énergétique produisent-elles des effets mesurables ?**\n
**Comment se situe votre commune, votre département ou votre région sur ces enjeux clés ?**

---

### 📊 À propos de cette application

Cette application interactive, construite à partir de **données publiques officielles**, vous permet d’explorer  
les **données de production et de consommation d’électricité** sur la période **2013–2022**  
*(les années suivantes ne sont pas encore disponibles)*.

Les indicateurs sont disponibles à différents niveaux territoriaux :
- 🏘️ **Commune**
- 🏛️ **Département**
- 🌐 **Région**

### 💡 Le saviez-vous ?  
🔹 En 2022, seulement **15,8 %** de l’électricité consommée en France métropolitaine provenait de sources renouvelables.  
  
🔹 La commune ayant la plus forte production renouvelable était **Villeurbanne (69)**, grâce à son barrage hydraulique.  
  
🔹 **L’Aube** était le seul département produisant plus d’électricité renouvelable qu’il n’en consommait, grâce à l’éolien.



### 🧭 Comment naviguer

Utilisez le **menu de gauche** pour accéder aux différentes vues :

- 🇫🇷 **France 2022** – Vue nationale de référence  
- 🏘️ **Par commune** – Analyse locale détaillée  
- 🏛️ **Par département** – Comparaison territoriale  
- 🌐 **Par région** – Vision macro-énergétique  
- 📋 **Données détaillées** – Tableaux et classements

---

ℹ️ *Les graphiques et indicateurs s’adaptent automatiquement à vos sélections (zone, période).*
"""
)

st.markdown("---")

st.markdown(
    """
### 🔗 Sources des données

Pour la réalisation de ce bilan, les jeux de données officiels suivants ont été utilisés :

* 📊 **Données Énergie (Data.gouv.fr)** : [Portail global des données de l'énergie](https://www.data.gouv.fr/pages/donnees-energie/)
* ⚡ **Production** : [Production électrique annuelle par filière à la maille commune](https://www.data.gouv.fr/datasets/production-electrique-annuelle-par-filiere-a-la-maille-commune/)
* 🔌 **Consommation** : [Consommation annuelle d'électricité et gaz par commune](https://www.data.gouv.fr/datasets/consommation-annuelle-delectricite-et-gaz-par-commune/)
* 👥 **Démographie** : [Population municipale des communes (INSEE)](https://www.data.gouv.fr/datasets/population-municipale-des-communes-france-entiere/) & [Statistiques détaillées](https://www.insee.fr/fr/statistiques/8581810?sommaire=8581933)
* 🗺️ **Géographie** : [API Découpage administratif (Etalab)](https://geo.api.gouv.fr/decoupage-administratif)

---
"""
)
st.markdown("""
    <style>
        /* Supprime la limite de hauteur de la liste des pages */
        [data-testid="stSidebarNav"] {
            max-height: none !important;
        }
        /* Optionnel : réduit l'espace vide tout en haut de la sidebar */
        [data-testid="stSidebarNav"] ul {
            padding-top: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        """
        **👤 Auteur**  
        *Caroline NARDY*  

        📧 [caroline.nardy@orange.fr](mailto:caroline.nardy@orange.fr)  
        🔗 [LinkedIn](https://www.linkedin.com/in/caroline-nardy/)  
        💻 [GitHub](https://github.com/Caro38290)
        """
    )
