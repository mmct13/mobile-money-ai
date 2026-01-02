import streamlit as st
import pandas as pd
import json
import time
import os
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION PAGE (Largeur max) ---
st.set_page_config(
    page_title="MoneyShield CI | Protection Fraude Mobile Money",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PREMIUM (Thème Moderne) ---
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* Fond global avec gradient subtil */
    .stApp {
        background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
        color: #212529;
        font-family: 'Inter', sans-serif;
    }
    
    /* Cartes métriques premium avec glassmorphism */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(222, 226, 230, 0.6);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
        border-color: rgba(25, 135, 84, 0.3);
    }
    
    /* Animation de pulse pour les valeurs */
    div[data-testid="metric-container"] > div > div {
        animation: fadeIn 0.6s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Labels des métriques */
    div[data-testid="metric-container"] label {
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6C757D !important;
    }
    
    /* Valeurs des métriques */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #198754 !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Titres avec gradient */
    h1 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #198754 0%, #20C997 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2, h3 {
        font-family: 'Poppins', sans-serif;
        color: #212529;
        font-weight: 600;
    }
    
    h4 {
        font-family: 'Inter', sans-serif;
        color: #495057;
        font-weight: 500;
    }
    
    /* Sidebar premium */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F8F9FA 100%);
        border-right: 1px solid rgba(222, 226, 230, 0.8);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.04);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }
    
    /* Filtres sidebar */
    .stSelectbox > label {
        font-weight: 600 !important;
        color: #495057 !important;
        font-size: 0.9rem !important;
    }
    
    /* Tableaux modernes */
    .dataframe {
        font-size: 14px !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #198754 0%, #20C997 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px !important;
        text-transform: uppercase;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px;
    }
    
    .dataframe tbody tr:hover {
        background-color: rgba(25, 135, 84, 0.05) !important;
        transition: background-color 0.2s ease;
    }
    
    /* Icônes personnalisées avec animation */
    .custom-icon {
        font-size: 1.3em;
        margin-right: 10px;
        vertical-align: middle;
        display: inline-block;
        transition: transform 0.3s ease;
    }
    
    h1:hover .custom-icon, h2:hover .custom-icon, h3:hover .custom-icon {
        transform: scale(1.1) rotate(5deg);
    }
    
    /* Badge de statut animé */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .status-live {
        background: linear-gradient(135deg, #198754 0%, #20C997 100%);
        color: white;
    }
    
    /* Séparateurs stylisés */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #DEE2E6 50%, transparent 100%);
    }
    
    /* Graphiques Plotly */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        background: white;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    }
    
    /* En-tête de section */
    .section-header {
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(25, 135, 84, 0.2);
    }
    
    /* Animation de chargement */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    .loading {
        background: linear-gradient(90deg, #F8F9FA 0%, #E9ECEF 50%, #F8F9FA 100%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
FICHIER_DB = os.path.join(DOSSIER_COURANT, "alertes_db.json")

# --- MAPPING COULEURS OPERATEURS (Authentique) ---
COULEURS_OPS = {
    "Orange Money": "#FF7900",  # Orange Officiel
    "MTN MoMo": "#FFCC00",      # Jaune MTN
    "Moov Money": "#009933",    # Vert Moov
    "Wave": "#1E90FF",          # Bleu Wave
    "INCONNU": "#808080"
}


def charger_donnees():
    if not os.path.exists(FICHIER_DB):
        return pd.DataFrame()
    try:
        with open(FICHIER_DB, 'r') as f:
            data = json.load(f)
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()


# --- HEADER ---
c1, c2, c3 = st.columns([2, 4, 2])
with c1:
    st.markdown("# <i class='bi bi-shield-fill custom-icon'></i>MoneyShield CI", unsafe_allow_html=True)
with c2:
    st.markdown("<h4 style='margin-top: 1rem; color: #6C757D;'>Plateforme Intelligente de Protection Anti-Fraude Mobile Money</h4>", unsafe_allow_html=True)
with c3:
    st.markdown("<div style='text-align: right; margin-top: 1rem;'><span class='status-badge status-live'><i class='bi bi-broadcast'></i> Live</span></div>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR FILTRES ---
st.sidebar.markdown("### <i class='bi bi-funnel custom-icon'></i> Filtres d'Analyse", unsafe_allow_html=True)

# Charger les données
df = charger_donnees()

if df.empty:
    st.info("En attente de flux... (Démarrez le simulateur)")
else:
    # Options de filtre
    villes_dispo = ["Toutes"] + sorted(df['ville'].unique().tolist())
    ops_dispo = ["Tous"] + sorted(df['operateur'].unique().tolist())

    choix_ville = st.sidebar.selectbox("Commune / Ville", villes_dispo, key="filter_ville")
    choix_op = st.sidebar.selectbox("Opérateur", ops_dispo, key="filter_op")

    # 1. FILTRAGE
    df_filtre = df.copy()
    if choix_ville != "Toutes":
        df_filtre = df_filtre[df_filtre['ville'] == choix_ville]
    if choix_op != "Tous":
        df_filtre = df_filtre[df_filtre['operateur'] == choix_op]

    # 2. KPIs (PREMIUM CARDS)
    st.markdown("<div class='section-header'><h3><i class='bi bi-speedometer2 custom-icon'></i>Tableau de Bord Analytique</h3></div>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    
    total_fraude = df_filtre['montant'].sum()
    nb_alertes = len(df_filtre)
    
    # Calcul robuste de la zone critique
    if not df_filtre.empty and len(df_filtre['ville'].unique()) > 0:
        mode_ville = df_filtre['ville'].mode()
        top_ville = mode_ville[0] if len(mode_ville) > 0 else df_filtre['ville'].iloc[0]
    else:
        top_ville = "N/A"
    
    # Calcul robuste du canal vulnérable
    if 'canal' in df_filtre.columns and not df_filtre.empty and len(df_filtre['canal'].unique()) > 0:
        mode_canal = df_filtre['canal'].mode()
        top_canal = mode_canal[0] if len(mode_canal) > 0 else df_filtre['canal'].iloc[0]
    else:
        top_canal = "N/A"

    k1.metric("🚨 Alertes Détectées", nb_alertes, f"{nb_alertes} transactions suspectes")
    k2.metric("💰 Montant à Risque", f"{total_fraude:,.0f} F".replace(",", " "), "Francs CFA")
    k3.metric("📍 Zone Critique", top_ville, "Concentration maximale")
    k4.metric("📱 Canal Vulnérable", top_canal, "Vecteur d'attaque")

    st.markdown("---")

    # 3. GRAPHIQUES AVANCES
    g1, g2 = st.columns([2, 1])

    with g1:
        st.markdown("<div class='section-header'><h4><i class='bi bi-globe custom-icon'></i>Cartographie Géographique des Menaces</h4></div>", unsafe_allow_html=True)
        if not df_filtre.empty:
            try:
                # Si on n'a pas la colonne canal, on gère l'erreur
                path = ['ville', 'operateur']
                if 'canal' in df_filtre.columns:
                    path.append('canal')

                fig_tree = px.sunburst(
                    df_filtre,
                    path=path,
                    values='montant',
                    color='operateur',
                    color_discrete_map=COULEURS_OPS,
                    title="Hiérarchie : Ville > Opérateur > Canal"
                )
                fig_tree.update_layout(margin=dict(t=30, l=0, r=0, b=0), height=400)
                st.plotly_chart(fig_tree, use_container_width=True, key="sunburst_main")
            except Exception as e:
                st.warning(f"Pas assez de données pour afficher le graphique de cartographie.")

    with g2:
        st.markdown("<div class='section-header'><h4><i class='bi bi-pie-chart-fill custom-icon'></i>Répartition par Opérateur</h4></div>", unsafe_allow_html=True)
        if not df_filtre.empty:
            try:
                # Pie Chart avec les vraies couleurs
                fig_pie = px.pie(
                    df_filtre, 
                    names='operateur', 
                    values='montant',
                    color='operateur',
                    color_discrete_map=COULEURS_OPS,
                    hole=0.6
                )
                fig_pie.update_layout(showlegend=False, height=400, margin=dict(t=30, l=0, r=0, b=0))
                st.plotly_chart(fig_pie, use_container_width=True, key="pie_main")
            except Exception as e:
                st.warning(f"Pas assez de données pour afficher la distribution des opérateurs.")

    # 4. TABLEAU DETAILLE
    st.markdown("<div class='section-header'><h4><i class='bi bi-table custom-icon'></i>Journal des Transactions Suspectes</h4></div>", unsafe_allow_html=True)
    
    # Sélection intelligente des colonnes
    cols = ['date_heure', 'ville', 'operateur', 'canal', 'type', 'montant', 'expediteur', 'motif', 'score']
    cols_dispo = [c for c in cols if c in df_filtre.columns]
    
    st.dataframe(
        df_filtre[cols_dispo].sort_values(by='date_heure', ascending=False),
        use_container_width=True,
        height=300
    )

# Auto-refresh toutes les 2 secondes
time.sleep(2)
st.rerun()