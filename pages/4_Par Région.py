# Importation des bibliothèques nécessaires
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Bilan Energetique Par Région", layout="wide")

st.header("⚡ Evolution Bilan Énergétique et Part des Renouvelables")
st.header("-- Par Région --")
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

# Créer une table de dimension "communes" qui servira de slicer
dim_communes = (
    df_conso[[
        "code_commune",
        "nom_commune",
        "code_departement",
        "nom_departement",
        "code_region",
        "nom_region"
    ]]
    .drop_duplicates()
)

# Sélection de la région via un selectbox dans streamlit


region_selectionnee = st.selectbox(
    "Sélectionner une région",
    sorted(dim_communes["nom_region"].unique())
)

annees_disponibles = sorted(df_conso["annee"].unique())
min_annee, max_annee = min(annees_disponibles), max(annees_disponibles)

periode = st.slider(
    "Sélectionnez la période",
    min_value=min_annee,
    max_value=max_annee,
    value=(min_annee, max_annee),
    step=1
)

annee_debut, annee_fin = periode

# Filtrer les données en fonction de la région et de la période sélectionnées
# Problème: les codes région dans df_pop ne sont pas les mêmes que ceux des autres df; il faut donc récupérer la liste des codes communes
# appartenant à la région sélectionnée dans dim_communes puis filtrer df_pop en fonction de ces codes communes

@st.cache_data
def compute_region_data(region_selectionnee, annee_debut, annee_fin, dim_communes, df_conso, df_prod, df_pop):
        codes_communes_region = set(
            dim_communes[dim_communes["nom_region"] == region_selectionnee]["code_commune"]
        )

        df_conso_filtre = df_conso[
                (df_conso["code_commune"].isin(codes_communes_region)) &
                df_conso["annee"].between(annee_debut, annee_fin)
            ]

        df_prod_filtre = df_prod[
                (df_prod["code_commune"].isin(codes_communes_region)) &
                df_prod["annee"].between(annee_debut, annee_fin)
            ]

        df_pop_filtre = df_pop[
                (df_pop["code_commune"].isin(codes_communes_region)) &
                df_pop["annee"].between(annee_debut, annee_fin)
            ]
        return codes_communes_region,df_conso_filtre, df_prod_filtre, df_pop_filtre

with st.spinner("Calcul des indicateurs pour la région sélectionnée..."):
            codes_communes_region,df_conso_filtre, df_prod_filtre, df_pop_filtre = compute_region_data(
                region_selectionnee,
                annee_debut,
                annee_fin,
                dim_communes,
                df_conso,
                df_prod,
                df_pop
            )
            if not codes_communes_region:
                st.error("Aucune commune trouvée pour cette région.")
                st.stop()


# Créer les différents KPI et graphiques qui seront utilisés sur les pages Commune / Département / Région
# A noter que les filtres de sélection (selectbox) ont été implémentés directement dans les pages correspondantes et les df ont été filtrés 
# en conséquence

# Calcul de la consommation totale pour la commune sélectionnée et la période sélectionnée
conso_totale_commune = df_conso_filtre['Conso totale (MWh)'].sum()

# Calcul de l'évolution de la consommation totale pour la commune sélectionnée entre le début et la fin de la période sélectionnée
evolution_conso_commune = None
conso_debut = df_conso_filtre[df_conso_filtre['annee'] == annee_debut]['Conso totale (MWh)'].sum()
conso_fin = df_conso_filtre[df_conso_filtre['annee'] == annee_fin]['Conso totale (MWh)'].sum()
if conso_debut > 0:
    evolution_conso_commune = ((conso_fin - conso_debut) / conso_debut) * 100

# Calcul de la production totale pour la commune sélectionnée et la période sélectionnée
prod_totale_commune = df_prod_filtre['prod_totale'].sum()

# Calcul de l'évolution de la production totale pour la commune sélectionnée entre le début et la fin de la période sélectionnée
evolution_prod_commune = None
prod_debut = df_prod_filtre[df_prod_filtre['annee'] == annee_debut]['prod_totale'].sum()
prod_fin = df_prod_filtre[df_prod_filtre['annee'] == annee_fin]['prod_totale'].sum()
if prod_debut > 0:
    evolution_prod_commune = ((prod_fin - prod_debut) / prod_debut) * 100

# Fonction de formatage des nombres en français avec espace comme séparateur de milliers
def format_fr(valeur):
    return f"{valeur:,.0f}".replace(",", " ")




# Pourcentage de la production par rapport à la consommation pour la commune sélectionnée et la période sélectionnée
if conso_totale_commune > 0:
    pourcentage_prod_conso_commune = (prod_totale_commune / conso_totale_commune) * 100
else:
    pourcentage_prod_conso_commune = 0

# Créer une jauge plotly pour le pourcentage de la production par rapport à la consommation pour la commune sélectionnée et la période sélectionnée
fig_gauge_prod_conso_commune = go.Figure(
    go.Indicator(
        value=pourcentage_prod_conso_commune,
        title={'text': "Pourcentage de la production par rapport à la consommation"},
        mode="gauge+number",
        number={'suffix': " %"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "green"}            
        }
    )
)

# Calcul de l'évolution du pourcentage de la production par rapport à la consommation entre le début et la fin de la période sélectionnée
pourcentage_debut = None
pourcentage_fin = None
conso_debut = df_conso_filtre[df_conso_filtre['annee'] == annee_debut]['Conso totale (MWh)'].sum()
prod_debut = df_prod_filtre[df_prod_filtre['annee'] == annee_debut]['prod_totale'].sum()
if conso_debut > 0:
    pourcentage_debut = (prod_debut / conso_debut) * 100
conso_fin = df_conso_filtre[df_conso_filtre['annee'] == annee_fin]['Conso totale (MWh)'].sum()
prod_fin = df_prod_filtre[df_prod_filtre['annee'] == annee_fin]['prod_totale'].sum()
if conso_fin > 0:
    pourcentage_fin = (prod_fin / conso_fin) * 100
evolution_pourcentage_prod_conso = None
if pourcentage_debut is not None and pourcentage_fin is not None and pourcentage_debut > 0:
    evolution_pourcentage_prod_conso = ((pourcentage_fin - pourcentage_debut) / pourcentage_debut) * 100
st.write(f"### Données pour la région {region_selectionnee} de {annee_debut} à {annee_fin}")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Consommation totale (MWh)", f"{format_fr(conso_totale_commune)} MWh")
with col2:
    st.metric("% Renouvelable", f"{pourcentage_prod_conso_commune:.2f} %")
with col3:
    st.metric("Production totale (MWh)", f"{format_fr(prod_totale_commune)} MWh")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Evolution de la consommation sur la période", f"{evolution_conso_commune:.2f} %")
with col2:
    st.metric("Evolution de la part du renouvelable sur la période", f"{evolution_pourcentage_prod_conso:.2f} %")
with col3:
    st.metric("Evolution de la production totale sur la période", f"{evolution_prod_commune:.2f} %")

st.markdown("---")
#st.plotly_chart(fig_gauge_prod_conso_commune, use_container_width=True)


# Créer un PIE CHART de la répartition de la consommation par secteur pour la commune sélectionnée et la période sélectionnée   
conso_secteur_commune = df_conso_filtre.groupby('CODE GRAND SECTEUR', as_index=False)['Conso totale (MWh)'].sum()
fig_conso_secteur_commune = px.pie(
    conso_secteur_commune,
    names='CODE GRAND SECTEUR',
    values='Conso totale (MWh)',
    #title=f'Consommation par secteur',
    hole=0.3
)
fig_conso_secteur_commune.update_traces(
    textposition='outside',
    textinfo='percent+label'
)
fig_conso_secteur_commune.update_layout(
    showlegend=False,
    margin=dict(t=80, b=40, l=80, r=80)
    )




# Créer un PIE CHART de production par filière pour la commune sélectionnée et la période sélectionnée

mapping_filieres = {
    "prod_photovoltaique": "Photovoltaïque",
    "prod_eolien": "Éolien",
    "prod_hydraulique": "Hydraulique",
    "prod_bio_energie": "Bioénergie",
    "prod_cogeneration": "Cogénération",
    "prod_autres_filieres": "Autres filières"
}

prod_filiere_commune = (
    df_prod_filtre[list(mapping_filieres.keys())]
    .sum()
    .reset_index()
)

prod_filiere_commune.columns = ["Filière", "Production (MWh)"]

# Renommer les filières
prod_filiere_commune["Filière"] = prod_filiere_commune["Filière"].map(mapping_filieres)

# Supprimer les valeurs nulles ou égales à 0
prod_filiere_commune = prod_filiere_commune[
    prod_filiere_commune["Production (MWh)"] > 0
]

fig_prod_filiere_commune = px.pie(
    prod_filiere_commune,
    names="Filière",
    values="Production (MWh)",
    hole=0.3
)

fig_prod_filiere_commune.update_traces(
    textinfo="percent+label",
    textposition="outside"
)

fig_prod_filiere_commune.update_layout(
    showlegend=False,
    margin=dict(t=80, b=40, l=80, r=80)
    )

col1, col2 = st.columns(2)
with col1:
    st.write("##### Consommation par secteur")
with col2:
    st.write("##### Production par filière")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_conso_secteur_commune, use_container_width=True)
with col2:
    st.plotly_chart(fig_prod_filiere_commune, use_container_width=True)

st.markdown("---")

# Créer un line chart montrant trois indicateurs: evolution de la production par habitant, évolution de la consommation par habitant et
# évolution de la population pour la commune sélectionnée et la période sélectionnée

df_evolution = (
    df_conso_filtre
    .groupby("annee", as_index=False)
    .agg({
        "Conso totale (MWh)": "sum"
    })
    .merge(
        df_prod_filtre.groupby("annee", as_index=False)
        .agg({"prod_totale": "sum"}),
        on="annee"
    )
    .merge(
        df_pop_filtre.groupby("annee", as_index=False)
        .agg({"Population": "sum"}),  
        on="annee"
    )
)

df_evolution["conso_par_habitant"] = (
    df_evolution["Conso totale (MWh)"] / df_evolution["Population"]
)

df_evolution["prod_par_habitant"] = (
    df_evolution["prod_totale"] / df_evolution["Population"]
)

df_evolution = df_evolution.sort_values("annee")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_evolution["annee"],
        y=df_evolution["prod_par_habitant"],
        name="Production par habitant",
        mode="lines+markers"
    )
)

fig.add_trace(
    go.Scatter(
        x=df_evolution["annee"],
        y=df_evolution["conso_par_habitant"],
        name="Consommation par habitant",
        mode="lines+markers"
    )
)

fig.add_trace(
    go.Scatter(
        x=df_evolution["annee"],
        y=df_evolution["Population"],
        name="Population",
        mode="lines+markers",
        yaxis="y2"
    )
)

fig.update_layout(
    xaxis_title="Année",
    yaxis=dict(title="MWh / habitant"),
    yaxis2=dict(
        title="Nb habitants",
        overlaying="y",
        side="right"
    ),
    legend=dict(orientation="h", y=-0.2),
    margin=dict(t=80, l=60, r=60, b=80)
)

st.write("##### Évolution de la production et de la consommation par habitant vs Evolution du nombre d'habitants")
st.plotly_chart(fig, use_container_width=True)



