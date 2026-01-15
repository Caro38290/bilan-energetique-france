# Importation des bibliothèques nécessaires
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


st.set_page_config(
    page_title="Bilan Energetique et Part des Renouvelables", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.header("⚡ Evolution Bilan Énergétique et Part des Renouvelables")
st.header("-- Données détaillées et Classements --")
st.markdown("---")


# Chargement des données avec cache pour optimiser les performances
@st.cache_data
def load_data():
    df_conso = pd.read_parquet("data/df_conso_final.parquet")
    df_prod = pd.read_parquet("data/df_prod_final.parquet")
    df_pop = pd.read_csv("data/df_pop_final.csv", sep=";", encoding="utf-8")
    return df_conso, df_prod, df_pop

with st.spinner("Chargement des données..."):
        df_conso, df_prod, df_pop = load_data()

annees_disponibles = sorted(df_conso["annee"].unique())
min_annee, max_annee = min(annees_disponibles), max(annees_disponibles)



# Sélection de la zone territoriale et de la période
zone= st.radio(
    "Sélectionnez la zone territoriale", 
    ["Région", "Département", "Commune"]
    )

periode = st.slider(
    "Sélectionnez la période",
    min_value=min_annee,
    max_value=max_annee,
    value=(min_annee, max_annee),
    step=1
)

annee_debut, annee_fin = periode

# Créer le dataframe à afficher en cas de sélection "Commune". Les colonnes doivent être Nom Commune, Code Département, Conso totale, 
# Prod totale, population, ratio d'autoproduction
# Les données doivent être filtrées selon la période souhaitée et agrégées selon les colonnes

if zone == "Commune":
    df_conso_filtre = df_conso[
        (df_conso["annee"].between(annee_debut, annee_fin))
    ]
    df_prod_filtre = df_prod[
        (df_prod["annee"].between(annee_debut, annee_fin))
    ]
    df_pop_filtre = df_pop[
        (df_pop["annee"].between(annee_debut, annee_fin))
    ]

    df_agg_conso = (
        df_conso_filtre
        .groupby("code_commune", as_index=False)["Conso totale (MWh)"]
        .sum()
    )
    df_agg_prod = (
        df_prod_filtre
        .groupby("code_commune", as_index=False)["prod_totale"]
        .sum()
    )
    df_agg_pop = (
        df_pop_filtre
        .groupby("code_commune", as_index=False)["Population"]
        .mean() # on utilise la moyenne puisqu'on raisonne au niveau communal
    )

    df_resultat = pd.merge(df_agg_conso, df_agg_prod, on="code_commune", how="left")
    df_resultat = pd.merge(df_resultat, df_agg_pop, on="code_commune", how="left")

    df_resultat["ratio_autoproduction"] = (
        df_resultat["prod_totale"] / df_resultat["Conso totale (MWh)"]
    ) * 100

    # Ajouter les colonnes Nom Commune et Code Département en récupérant les données du df_conso
    dim_communes = df_conso[["code_commune", "nom_commune", "code_departement"]].drop_duplicates()
    df_resultat = pd.merge(df_resultat, dim_communes, on="code_commune", how="left")

    # supprimer les lignes dont le nom de la commune est manquant, remplir les valeurs manquantes par 0,
    # et formater le code département pour qu'il ait toujours 2 chiffres
    df_resultat = df_resultat.dropna(subset=["nom_commune"])
    df_resultat = df_resultat.fillna(0)
    df_resultat["code_departement"] = df_resultat["code_departement"].astype(str).str.zfill(2)

    
    st.header("Données détaillées par commune")

    st.dataframe(
        df_resultat,
        column_order=(
            "nom_commune", "code_departement", "Conso totale (MWh)", 
            "prod_totale", "Population", "ratio_autoproduction"
        ),
        column_config={
            "nom_commune": "Nom Commune",
            "code_departement": "Code Département",
            "Conso totale (MWh)": st.column_config.NumberColumn(
                "Conso totale (MWh)", 
                format="%.2f"
            ),
            "prod_totale": st.column_config.NumberColumn(
                "Prod totale (MWh)", 
                format="%.2f"
            ),
            "Population": st.column_config.NumberColumn(
                "Population moyenne", 
                format="%d"
            ),
            "ratio_autoproduction": st.column_config.NumberColumn(
                "Ratio d'autoproduction (%)", 
                format="%.2f%%"
            ),
        },
        use_container_width=True,
        hide_index=True
    )
if zone == "Département":
    df_conso_filtre = df_conso[
        (df_conso["annee"].between(annee_debut, annee_fin))
    ]
    df_prod_filtre = df_prod[
        (df_prod["annee"].between(annee_debut, annee_fin))
    ]
    df_pop_filtre = df_pop[
        (df_pop["annee"].between(annee_debut, annee_fin))
    ]

    df_agg_conso = (
        df_conso_filtre
        .groupby("code_departement", as_index=False)["Conso totale (MWh)"]
        .sum()
    )
    df_agg_prod = (
        df_prod_filtre
        .groupby("code_departement", as_index=False)["prod_totale"]
        .sum()
    )
    # Pour la population, on doit faire une agrégation en deux étapes:
    # 1. On somme par département ET par année pour avoir le total du département chaque année
    df_pop_annuelle = (
        df_pop_filtre
        .groupby(["code_departement", "annee"], as_index=False)["Population"]
        .sum()
    )

    # 2. On fait la moyenne de ces totaux sur la période
    df_agg_pop = (
        df_pop_annuelle
        .groupby("code_departement", as_index=False)["Population"]
        .mean()
    )

    df_resultat = pd.merge(df_agg_conso, df_agg_prod, on="code_departement", how="left")
    df_resultat = pd.merge(df_resultat, df_agg_pop, on="code_departement", how="left")

    df_resultat["ratio_autoproduction"] = (
        df_resultat["prod_totale"] / df_resultat["Conso totale (MWh)"]
    ) * 100

    # Ajouter les colonnes Nom Département et Code Région en récupérant les données du df_conso
    dim_departements = df_conso[["code_departement", "nom_departement", "code_region"]].drop_duplicates()
    df_resultat = pd.merge(df_resultat, dim_departements, on="code_departement", how="left")

    # supprimer les lignes dont le nom du département est manquant, remplir les valeurs manquantes par 0,
    # et formater le code région pour qu'il ait toujours 2 chiffres
    df_resultat = df_resultat.dropna(subset=["nom_departement"])
    df_resultat = df_resultat.fillna(0)
    df_resultat["code_departement"] = df_resultat["code_departement"].astype(str).str.zfill(2)

    
    st.header("Données détaillées par département")

    st.dataframe(
        df_resultat,
        column_order=(
            "nom_departement", "code_departement", "Conso totale (MWh)", 
            "prod_totale", "Population", "ratio_autoproduction"
        ),
        column_config={
            "nom_departement": "Nom Département",
            "code_departement": "Code Département",
            "Conso totale (MWh)": st.column_config.NumberColumn(
                "Conso totale (MWh)", 
                format="%.2f"
            ),
            "prod_totale": st.column_config.NumberColumn(
                "Prod totale (MWh)", 
                format="%.2f"
            ),
            "Population": st.column_config.NumberColumn(
                "Population moyenne", 
                format="%d"
            ),
            "ratio_autoproduction": st.column_config.NumberColumn(
                "Ratio d'autoproduction (%)", 
                format="%.2f%%"
            ),
        },
        use_container_width=True,
        hide_index=True
    )

if zone == "Région":

    # Filtrage par période uniquement
    df_conso_filtre = df_conso[df_conso["annee"].between(annee_debut, annee_fin)]
    df_prod_filtre = df_prod[df_prod["annee"].between(annee_debut, annee_fin)]
    df_pop_filtre  = df_pop[df_pop["annee"].between(annee_debut, annee_fin)]

    # =============================
    # Agrégation consommation
    # =============================
    df_agg_conso = (
        df_conso_filtre
        .groupby("code_region", as_index=False)["Conso totale (MWh)"]
        .sum()
    )

    # =============================
    # Agrégation production
    # =============================
    df_agg_prod = (
        df_prod_filtre
        .groupby("code_region", as_index=False)["prod_totale"]
        .sum()
    )

    # =============================
    # Agrégation population (2 étapes)
    # =============================
    # 1. Population totale régionale par année (en remplaçant le code_region erroné de df_pop_filtre par celui du conso)
    df_pop_annuelle = (
        df_pop_filtre
        .drop(columns=["code_region"], errors="ignore")  # ⬅️ on enlève le mauvais code
        .merge(
            df_conso[["code_commune", "code_region"]].drop_duplicates(),
            on="code_commune",
            how="left"
        )
        .groupby(["code_region", "annee"], as_index=False)["Population"]
        .sum()
    )


    # 2. Moyenne sur la période
    df_agg_pop = (
        df_pop_annuelle
        .groupby("code_region", as_index=False)["Population"]
        .mean()
    )

    # =============================
    # Fusion des indicateurs
    # =============================
    df_resultat = (
        df_agg_conso
        .merge(df_agg_prod, on="code_region", how="left")
        .merge(df_agg_pop, on="code_region", how="left")
    )

    # =============================
    # Calcul ratio d'autoproduction
    # =============================
    df_resultat["ratio_autoproduction"] = (
        df_resultat["prod_totale"] / df_resultat["Conso totale (MWh)"]
    ) * 100

    # =============================
    # Ajout nom de la région (dimension)
    # =============================
    dim_regions = (
        df_conso[["code_region", "nom_region"]]
        .drop_duplicates()
    )

    df_resultat = df_resultat.merge(
        dim_regions,
        on="code_region",
        how="left"
    )

    # Nettoyage
    df_resultat = df_resultat.dropna(subset=["nom_region"])
    df_resultat = df_resultat.fillna(0)
    df_resultat["code_region"] = df_resultat["code_region"].astype(str).str.zfill(2)

    # =============================
    # Affichage
    # =============================
    st.header("Données détaillées par région")

    st.dataframe(
        df_resultat,
        column_order=(
            "nom_region", "code_region",
            "Conso totale (MWh)", "prod_totale",
            "Population", "ratio_autoproduction"
        ),
        column_config={
            "nom_region": "Nom Région",
            "code_region": "Code Région",
            "Conso totale (MWh)": st.column_config.NumberColumn(
                "Conso totale (MWh)", format="%d"
            ),
            "prod_totale": st.column_config.NumberColumn(
                "Prod totale (MWh)", format="%d"
            ),
            "Population": st.column_config.NumberColumn(
                "Population moyenne", format="%d"
            ),
            "ratio_autoproduction": st.column_config.NumberColumn(
                "Ratio d'autoproduction (%)", format="%.2f%%"
            ),
        },
        use_container_width=True,
        hide_index=True
    )

st.write("A noter: Vous pouvez trier les données en cliquant sur les en-têtes de colonne et faire défiler les résultats à l'aide de l'ascenseur"
        "sur la droite du tableau.")

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

# Créer une carte chlorophète de la France montrant le ratio d'autoproduction par département pour la période sélectionnée
# Utiliser plotly.express.choropleth pour cela
# Charger le fichier geojson des départements français
@st.cache_data
def load_geojson_dept():
    import json
    with open("data/departements.geojson", "r", encoding="utf-8") as f:
        geojson_dept = json.load(f)
    return geojson_dept
geojson_dept = load_geojson_dept()
# Filtrer les données pour la période sélectionnée
df_conso_dept = df_conso[
    (df_conso["annee"].between(annee_debut, annee_fin))
].groupby(
    ["code_departement"], as_index=False
)["Conso totale (MWh)"].sum()
df_prod_dept = df_prod[
    (df_prod["annee"].between(annee_debut, annee_fin))
].groupby(
    ["code_departement"], as_index=False
)["prod_totale"].sum()
df_ratio_autoprod_dept = pd.merge(
    df_conso_dept,
    df_prod_dept,
    on="code_departement"
)

# On convertit en string et on complète avec un '0' pour avoir 2 caractères (ex: '1' -> '01')
df_ratio_autoprod_dept["code_departement"] = df_ratio_autoprod_dept["code_departement"].astype(str).str.zfill(2)

df_ratio_autoprod_dept["ratio_autoproduction"] = (
    df_ratio_autoprod_dept["prod_totale"] / df_ratio_autoprod_dept["Conso totale (MWh)"]
) * 100
fig = px.choropleth(
    df_ratio_autoprod_dept,
    geojson=geojson_dept,
    locations="code_departement",
    color="ratio_autoproduction",
    color_continuous_scale="Viridis",
    range_color=(0, 100),
    featureidkey="properties.code",
    projection="mercator",
    labels={"ratio_autoproduction": "Ratio d'autoproduction (%)"},
    title=f"Ratio d'autoproduction par département ({annee_debut}-{annee_fin})"
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

     