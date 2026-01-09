# Importation des bibliothèques nécessaires
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Bilan Énergétique", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ Bilan Énergétique et Part des Renouvelables")
st.subheader("France métropolitaine – 2022")
st.markdown("---")

# Chargement des données avec cache pour optimiser les performances
@st.cache_data
def load_data():
    df_conso = pd.read_csv("data/df_conso_final.csv", sep=";", encoding="utf-8")
    df_prod = pd.read_csv("data/df_prod_final.csv", sep=";", encoding="utf-8")
    df_pop = pd.read_csv("data/df_pop_final.csv", sep=";", encoding="utf-8")
    return df_conso, df_prod, df_pop

with st.spinner("Chargement des données..."):
        df_conso, df_prod, df_pop = load_data()


# Préparation des KPI et graphiques

# Calcul de la consommation totale en 2022
conso_2022 = df_conso[df_conso['annee'] == 2022]['Conso totale (MWh)'].sum()
print(f"Consommation totale d'électricité en 2022: {conso_2022:,.2f} MWh".replace(",", " "))

# Calcul de la conso moyenne par habitant en 2022
conso2022ParHab= conso_2022 / df_pop[df_pop['annee'] == 2022]['Population'].sum()
print(f"Consommation moyenne par habitant en 2022: {conso2022ParHab:,.2f} MWh".replace(",", " "))

# Calcul de la production totale en 2022
prod_2022 = df_prod[df_prod['annee'] == 2022]['prod_totale'].sum()
print(f"Production totale d'électricité verte en 2022: {prod_2022:,.2f} MWh".replace(",", " "))

# Calcul de la prod moyenne par habitant en 2022
prod2022ParHab= prod_2022 / df_pop[df_pop['annee'] == 2022]['Population'].sum()
print(f"Production moyenne par habitant en 2022: {prod2022ParHab:,.2f} MWh".replace(",", " "))

# Pourcentage de la production par rapport à la consommation en 2022
pourcentage_prod_conso_2022 = (prod_2022 / conso_2022) * 100
print(f"Part d'électricité provenant de sources renouvelables en 2022: {pourcentage_prod_conso_2022:.2f}%")

# Créer un graphique plotly en barres horizontales de la consommation par secteur pour l'année 2022; Trier les résultats par ordre décroissant de consommation
# et afficher les étiquettes de valeur sur les barres 
import plotly.express as px
conso_secteur_2022 = (
    df_conso[df_conso['annee'] == 2022]
    .groupby('CODE GRAND SECTEUR', as_index=False)['Conso totale (MWh)']
    .sum()
    .sort_values(by='Conso totale (MWh)', ascending=False)
) # type: ignore

fig_conso_secteur = px.bar(
    conso_secteur_2022,
    x='Conso totale (MWh)',
    y='CODE GRAND SECTEUR',
    orientation='h',
    text='Conso totale (MWh)',
    title='Consommation par secteur en 2022'
)

fig_conso_secteur.update_traces(
    texttemplate='%{text:.2s}',
    textposition='inside'
)

fig_conso_secteur.update_yaxes(categoryorder='total ascending')

fig_conso_secteur.show()

# Créer un line chart plotly d'évolution de la consommation totale annuelle de 2013 à 2022 et l'afficher en ajoutant les étiquettes de valeur sur les points
evolution_conso_annuelle = (
    df_conso.groupby('annee', as_index=False)['Conso totale (MWh)'].sum()
)
fig_evolution_conso = px.line(
    evolution_conso_annuelle,
    x='annee',
    y='Conso totale (MWh)',
    title='Consommation totale (MWh) par Année',
    markers=True,
    text='Conso totale (MWh)'
)
fig_evolution_conso.update_traces(
    texttemplate='%{text:.2s}',
    textposition='top center'
)
fig_evolution_conso.show()

# Créer un pie chart plotly de la répartition de la production par filière en 2022 et l'afficher avec les noms des filières et valeurs sur les parts
mapping_filieres = {
    "prod_photovoltaique": "Photovoltaïque",
    "prod_eolien": "Éolien",
    "prod_hydraulique": "Hydraulique",
    "prod_bio_energie": "Bioénergie",
    "prod_cogeneration": "Cogénération",
    "prod_autres_filieres": "Autres filières"
}

prod_filiere_2022 = df_prod[df_prod['annee'] == 2022][
     list(mapping_filieres.keys())].sum().reset_index()
prod_filiere_2022.columns = ['Filière', 'Production (MWh)']
prod_filiere_2022["Filière"] = prod_filiere_2022["Filière"].map(mapping_filieres)
prod_filiere_2022["Production (MWh)"] = (
    prod_filiere_2022["Production (MWh)"] / 1e6
)
prod_filiere_2022 = prod_filiere_2022.rename(
    columns={"Production (MWh)": "Production (millions de MWh)"}
)


fig_prod_filiere = px.pie(
    prod_filiere_2022,
    names='Filière',
    values='Production (millions de MWh)',
    title='Production par filière renouvelable (MWh)',
    hole=0.3
)
fig_prod_filiere.update_traces(
    textposition='outside',
    texttemplate="%{label}<br>%{value:.1f} M<br>(%{percent})",
    hovertemplate="<b>%{label}</b><br>%{value:.2f} M MWh<br>%{percent}"
)
fig_prod_filiere.update_layout(showlegend=False)
fig_prod_filiere.show()

# Créer un line chart plotly d'évolution de la production totale annuelle de 2013 à 2022 et l'afficher en ajoutant les étiquettes de valeur sur les points
evolution_prod_annuelle = (
    df_prod.groupby('annee', as_index=False)['prod_totale'].sum()
)
fig_evolution_prod = px.line(
    evolution_prod_annuelle,
    x='annee',
    y='prod_totale',
    title='Production totale (MWh) par Année',
    markers=True,
    text='prod_totale'
)
fig_evolution_prod.update_traces(
    texttemplate='%{text:.2s}',
    textposition='top center'
)
fig_evolution_prod.show()

# Créer une jauge plotly pour le pourcentage de la production par rapport à la consommation en 2022
import plotly.graph_objects as go

fig_gauge_prod_conso = go.Figure(
    go.Indicator(
        value=pourcentage_prod_conso_2022,
        title={'text': "% d'électricité provenant de sources renouvelables en 2022"},
        mode="gauge+number",
        number={'suffix': " %"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "green"}            
        }
    )
)

fig_gauge_prod_conso.show()


# KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Consommation totale (MWh)", f"{conso_2022/1e6:.2f} M")
col2.metric("Conso par habitant (MWh)", f"{conso2022ParHab:.2f}")
col3.metric("Production renouvelable totale (MWh)", f"{prod_2022/1e6:.2f} M")
col4.metric("Prod par habitant (MWh)", f"{prod2022ParHab:.2f}")


st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_conso_secteur, width="stretch")

with col2:
    st.plotly_chart(fig_prod_filiere, width="stretch")

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_evolution_conso, width="stretch")

with col2:
    st.plotly_chart(fig_evolution_prod, width="stretch")

st.plotly_chart(fig_gauge_prod_conso, use_container_width=True)

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
