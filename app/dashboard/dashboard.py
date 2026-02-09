import streamlit as st
import pandas as pd
import time
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# --- NOUVEAUX IMPORTS (Architecture Modulaire) ---
# On utilise la connexion centralisée SQLite
try:
    from app.database import get_connection
except ImportError:
    # Fallback pour le dev local si lancé depuis le dossier dashboard
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.database import get_connection

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

# --- MAPPING COULEURS OPERATEURS ---
COULEURS_OPS = {
    "Orange Money": "#FF7900",  # Orange Officiel
    "MTN MoMo": "#FFCC00",      # Jaune MTN
    "Moov Money": "#009933",    # Vert Moov
    "Wave": "#1E90FF",          # Bleu Wave
    "INCONNU": "#808080"
}


# --- CONFIGURATION CARTE ---
VILLE_COORDS = {
    # Abidjan et ses communes
    "Abidjan-Plateau": {"lat": 5.3261, "lon": -4.0197},
    "Abidjan-Yopougon": {"lat": 5.3789, "lon": -4.0883},
    "Abidjan-Abobo": {"lat": 5.4322, "lon": -4.0205},
    "Abidjan-Cocody": {"lat": 5.3486, "lon": -3.9798},
    "Abidjan-Koumassi": {"lat": 5.2974, "lon": -3.9452},
    "Abidjan-Adjamé": {"lat": 5.3582, "lon": -4.0267},
    "Abidjan-Marcory": {"lat": 5.2982, "lon": -3.9752},
    "Abidjan-Treichville": {"lat": 5.2894, "lon": -4.0044},
    "Abidjan-Port-Bouët": {"lat": 5.2530, "lon": -3.9317},
    
    # Villes de l'intérieur
    "Bouaké": {"lat": 7.6925, "lon": -5.0232},
    "Daloa": {"lat": 6.8770, "lon": -6.4502},
    "Yamoussoukro": {"lat": 6.8206, "lon": -5.2767},
    "San-Pédro": {"lat": 4.7570, "lon": -6.6357},
    "Korhogo": {"lat": 9.4580, "lon": -5.6294},
    "Man": {"lat": 7.4116, "lon": -7.5566},
    "Gagnoa": {"lat": 6.1360, "lon": -5.9497},
    "Soubré": {"lat": 5.7856, "lon": -6.6083},
    "Séguéla": {"lat": 7.9626, "lon": -6.6717},
    "Odienné": {"lat": 9.5057, "lon": -7.5649},
    "Bondoukou": {"lat": 8.0384, "lon": -2.7981},
    "Aboisso": {"lat": 5.4674, "lon": -3.2081},
    "Bouaflé": {"lat": 6.9904, "lon": -5.7442},
    "Sassandra": {"lat": 4.9537, "lon": -6.0853}
}

def charger_donnees():
    """Charge les alertes depuis la base de données SQLite."""
    try:
        conn = get_connection()
        # On lit les 1000 dernières alertes pour ne pas surcharger le dashboard
        query = "SELECT * FROM alertes ORDER BY timestamp DESC LIMIT 1000"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return pd.DataFrame()
        
        # Harmonisation des noms de colonnes (SQL -> Dashboard)
        # Dans la DB c'est 'type_trans', le dashboard attend 'type'
        if 'type_trans' in df.columns:
            df.rename(columns={'type_trans': 'type'}, inplace=True)
            
        return df
    except Exception as e:
        # En prod, on peut logger l'erreur
        # st.error(f"Erreur de connexion BDD: {e}") 
        return pd.DataFrame()


def charger_transactions():
    """Charge TOUTES les transactions pour le dashboard financier."""
    try:
        conn = get_connection()
        # On lit les 5000 dernières transactions pour avoir de l'historique
        query = "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 5000"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def show_security_dashboard():
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

    # Charger les données via SQL
    df = charger_donnees()

    if df.empty:
        st.info("En attente de flux... (Assurez-vous que le Générateur et le Détecteur tournent)")
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
        
        # --- PREPARATION DONNEES CARTE ---
        # On agrège par ville pour avoir le total et le nombre
        df_map = df_filtre.groupby('ville').agg({
            'montant': 'sum',
            'timestamp': 'count', # count of alerts
            'operateur': lambda x: x.mode()[0] if not x.mode().empty else 'Mixte' # operateur principal
        }).rename(columns={'timestamp': 'nb_alertes'}).reset_index()

        # On ajoute les coords
        df_map['lat'] = df_map['ville'].map(lambda x: VILLE_COORDS.get(x, {}).get('lat'))
        df_map['lon'] = df_map['ville'].map(lambda x: VILLE_COORDS.get(x, {}).get('lon'))
        
        # On filtre les villes sans coords connues pour éviter les erreurs d'affichage
        df_map = df_map.dropna(subset=['lat', 'lon'])

        g1, g2 = st.columns([2, 1])

        with g1:
            st.markdown("<div class='section-header'><h4><i class='bi bi-map-fill custom-icon'></i>Carte des Zones Sensibles (Côte d'Ivoire)</h4></div>", unsafe_allow_html=True)
            if not df_map.empty:
                try:
                    # Carte Mapbox avec bulles
                    fig_map = px.scatter_mapbox(
                        df_map,
                        lat="lat",
                        lon="lon",
                        size="nb_alertes", # La taille des bulles dépend du nombre d'alertes
                        color="montant",   # La couleur dépend du montant de la fraude
                        hover_name="ville",
                        hover_data={"lat": False, "lon": False, "nb_alertes": True, "montant": True, "operateur": True},
                        color_continuous_scale=px.colors.sequential.Reds,
                        size_max=35,
                        zoom=5.5,
                        center={"lat": 7.54, "lon": -5.55} # Centre approximatif de la RCI
                    )

                    fig_map.update_layout(
                        mapbox_style="carto-positron", # Style clair, gratuit, pas besoin de token
                        margin=dict(t=0, l=0, r=0, b=0),
                        height=450
                    )
                    st.plotly_chart(fig_map, use_container_width=True, key="map_ci")
                except Exception as e:
                     st.warning(f"Erreur d'affichage de la carte: {e}")
            else:
                st.info("Aucune donnée géographique disponible pour les filtres actuels.")

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
                    fig_pie.update_layout(showlegend=False, height=450, margin=dict(t=20, l=20, r=20, b=20))
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

def show_financial_dashboard():
    # --- EN-TÊTE & CONTEXTE ---
    st.markdown("# <i class='bi bi-graph-up-arrow custom-icon'></i>Dashboard Financier", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #6C757D;'>Analyse des Volumes et Prévisions</h4>", unsafe_allow_html=True)
    
    # Texte explicatif simple pour non-techniciens
    st.markdown("""
    <div style='background-color: #e9ecef; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <strong>💡 À quoi sert cette page ?</strong><br>
        Cette section vous permet de suivre l'évolution financière des transactions mobile money. 
        Elle utilise l'intelligence artificielle pour anticiper les volumes futurs et identifier les périodes de forte activité.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    df = charger_transactions()
    
    if df.empty:
        st.info("En attente de transactions financières... (Le détecteur doit tourner)")
        return

    # Conversion de date_heure (Supporte les formats mixtes avec/sans microsecondes)
    df['date'] = pd.to_datetime(df['date_heure'], format='mixed')
    
    # --- 1. INDICATEURS CLES (KPIs) ---
    st.markdown("### <i class='bi bi-speedometer2 custom-icon'></i> Performance Globale", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    total_volume = df['montant'].sum()
    nb_trans = len(df)
    avg_ticket = df['montant'].mean() if nb_trans > 0 else 0
    
    col1.metric("💰 Volume Total", f"{total_volume:,.0f} F".replace(",", " "), delta_color="normal", help="Montant total des transactions traitées")
    col2.metric("💳 Nombre de Transactions", f"{nb_trans:.0f}", help="Nombre total d'opérations enregistrées")
    col3.metric("🏷️ Panier Moyen", f"{avg_ticket:,.0f} F".replace(",", " "), help="Montant moyen d'une transaction")
    
    st.markdown("---")

    # --- 2. ANALYSE TEMPORELLE (HEATMAP) ---
    c_heat, c_area = st.columns([1, 1])
    
    with c_heat:
        st.markdown("### <i class='bi bi-grid-3x3-gap-fill custom-icon'></i> Heures de Pointe", unsafe_allow_html=True)
        st.caption("Quand ont lieu le plus de transactions ?")
        
        if not df.empty:
            df['hour'] = df['date'].dt.hour
            df['day'] = df['date'].dt.day_name()
            # Ordre des jours
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            df['day'] = pd.Categorical(df['day'], categories=days_order, ordered=True)
            
            df_heat = df.groupby(['day', 'hour']).size().reset_index(name='count')
            
            fig_heat = px.density_heatmap(
                df_heat, 
                x='hour', 
                y='day', 
                z='count', 
                color_continuous_scale='Greens',
                labels={'day': 'Jour', 'hour': 'Heure', 'count': 'Volume'},
                title="Intensité des Transactions"
            )
            fig_heat.update_layout(height=400, margin=dict(t=30, l=0, r=0, b=0))
            st.plotly_chart(fig_heat, use_container_width=True)
            
            st.markdown("""
            <small style='color: #6c757d;'>
            🟥 <b>Lecture :</b> Les zones les plus foncées indiquent les moments de forte affluence. 
            Utilisez ces infos pour prévoir les pics de charge.
            </small>
            """, unsafe_allow_html=True)

    # --- 3. PARTS DE MARCHE (STACKED AREA) ---
    with c_area:
        st.markdown("### <i class='bi bi-layers-fill custom-icon'></i> Parts de Marché", unsafe_allow_html=True)
        st.caption("Évolution des volumes par opérateur")
        
        # Agrégation par heure et opérateur
        df_ops = df.set_index('date').groupby([pd.Grouper(freq='h'), 'operateur'])['montant'].sum().reset_index()
        
        if not df_ops.empty:
            fig_area = px.area(
                df_ops, 
                x='date', 
                y='montant', 
                color='operateur',
                color_discrete_map=COULEURS_OPS,
                labels={'montant': 'Volume (FCFA)', 'date': 'Temps'},
                title="Volume par Opérateur au fil du temps"
            )
            fig_area.update_layout(height=400, margin=dict(t=30, l=0, r=0, b=0), showlegend=True, legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_area, use_container_width=True)
            
            st.markdown("""
            <small style='color: #6c757d;'>
            🟦 <b>Lecture :</b> Ce graphique montre la contribution de chaque opérateur au volume total. 
            Idéal pour comparer la performance de Orange, MTN, Moov et Wave.
            </small>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # --- 4. PREVISIONS IA ---
    st.markdown("### <i class='bi bi-check-circle-fill custom-icon'></i> Prévisions Futures (IA)", unsafe_allow_html=True)
    
    # Agrégation par heure pour les courbes
    df_hourly = df.set_index('date').resample('h')['montant'].sum().reset_index()
    
    # --- LOGIQUE DE STABILISATION ---
    # Pour éviter que les prévisions changent à chaque refresh (5s), 
    # on n'entraîne le modèle que sur les HEURES COMPLÈTES passées.
    # L'heure courante (en cours) est exclue de l'entraînement car incomplète.
    
    current_time = pd.Timestamp.now()
    last_full_hour = current_time.floor('h') - pd.Timedelta(hours=1)
    
    # Données d'entraînement : jusqu'à la dernière heure complète
    df_train = df_hourly[df_hourly['date'] <= last_full_hour].copy()
    
    if len(df_train) > 24: 
        # --- FONCTION CACHÉE (Pour la performance et la stabilité) ---
        @st.cache_data(ttl=300) # Cache valide 5 minutes
        def predict_future_volumes(df_history):
            # 1. Feature Engineering
            df_ml = df_history.copy()
            df_ml['hour'] = df_ml['date'].dt.hour
            df_ml['dayofweek'] = df_ml['date'].dt.dayofweek
            df_ml['lag_1'] = df_ml['montant'].shift(1)
            df_ml = df_ml.dropna()
            
            if len(df_ml) < 10: return None, None
            
            X = df_ml[['hour', 'dayofweek', 'lag_1']]
            y = df_ml['montant']
            
            # 2. Entrainement
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # 3. Prédictions (Heure courante + 24h suivantes)
            future_preds = []
            
            # Point de départ : la dernière heure connue de l'historique d'entraînement
            last_known_date = df_history['date'].iloc[-1]
            last_known_val = df_history['montant'].iloc[-1]
            
            curr_date = last_known_date
            curr_lag = last_known_val
            
            # On prédit pour : Heure Courante + 24h Futures = 25 périodes
            for i in range(1, 26): 
                next_date = curr_date + pd.Timedelta(hours=1)
                
                next_features = pd.DataFrame([{
                    'hour': next_date.hour,
                    'dayofweek': next_date.dayofweek,
                    'lag_1': curr_lag
                }])
                
                pred = model.predict(next_features)[0]
                pred = max(0, pred)
                
                # Type de prévision
                lbl = 'Prévision (Heure en cours)' if next_date == current_time.floor('h') else 'Prévision (Futur)'
                
                future_preds.append({
                    'date': next_date,
                    'montant': pred,
                    'type': lbl
                })
                
                curr_date = next_date
                curr_lag = pred
                
            return pd.DataFrame(future_preds), model

        # Exécution de la prévision
        df_forecast, _ = predict_future_volumes(df_train)
        
        if df_forecast is not None:
            # --- AFFICHAGE / COMPARAISON ---
            
            # 1. Comparaison Heure Courante (Réel vs Prévu)
            current_hour_date = current_time.floor('h')
            
            # Réel (si dispo)
            real_current = df_hourly[df_hourly['date'] == current_hour_date]['montant'].sum() # Sera 0 si pas encore de transaction
            
            # Prévu
            pred_current_row = df_forecast[df_forecast['date'] == current_hour_date]
            pred_current = pred_current_row['montant'].iloc[0] if not pred_current_row.empty else 0
            
            delta_current = real_current - pred_current
            
            col_kpi_ia1, col_kpi_ia2 = st.columns(2)
            
            col_kpi_ia1.metric(
                "🎯 Heure en cours (Réel)", 
                f"{real_current:,.0f} F".replace(",", " "),
                delta=f"{delta_current:,.0f} F vs Prévision",
                help="Volume réel enregistré depuis le début de l'heure"
            )
            
            col_kpi_ia2.metric(
                "🤖 Heure en cours (Prévision IA)",
                f"{pred_current:,.0f} F".replace(",", " "),
                help="Ce que l'IA avait prévu pour cette heure (basé sur l'historique)"
            )
            
            # 2. Graphique Global
            # On combine : Historique Passé (Réel) + Prévisions
            df_display = pd.concat([
                df_train.assign(type='Historique (Réel)'),
                df_forecast
            ])
            
            # On ajoute le point "Réel" de l'heure courante pour la comparaison visuelle
            if real_current > 0:
                current_point = pd.DataFrame([{
                    'date': current_hour_date,
                    'montant': real_current,
                    'type': 'Temps Réel (En cours)'
                }])
                df_display = pd.concat([df_display, current_point])
            
            fig = px.line(df_display, x='date', y='montant', color='type',
                          title="Projection et Suivi Temps Réel",
                          color_discrete_map={
                              "Historique (Réel)": "#198754", # Vert
                              "Temps Réel (En cours)": "#dc3545", # Rouge (pour bien le voir)
                              "Prévision (Heure en cours)": "#ffc107", # Jaune
                              "Prévision (Futur)": "#0d6efd" # Bleu
                          })
            
            fig.update_traces(mode='lines+markers')
            # Pointillés pour le futur
            fig.for_each_trace(lambda t: t.update(line=dict(dash='dash')) if 'Prévision' in t.name else None)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Texte explicatif stable
            vol_next_24 = df_forecast[df_forecast['type'] == 'Prévision (Futur)']['montant'].sum()
            
            st.info(f"""
            ℹ️ **Analyse Stable :** 
            Pour les prochaines 24h, l'IA anticipe un volume total de **{vol_next_24:,.0f} F**.
            La prévision est mise à jour statiquement à chaque heure pile pour éviter les fluctuations.
            """)
            
        else:
            st.warning("Données insuffisantes pour la modélisation (besoin de plus d'historique stable).")
            st.line_chart(df_hourly.set_index('date')['montant'])
            
    else:
        st.info("Collecte d'historique en cours (Min. 24h d'heures COMPLÈTES requises)...")
        st.info(f"Heures complètes disponibles : {len(df_train)}")
        st.line_chart(df_hourly.set_index('date')['montant'])

# --- AUTHENTIFICATION RENFORCÉE ---
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# Récupération sécurisée des identifiants
SECURE_USER = os.getenv("ADMIN_USER", "admin")
SECURE_PWD = os.getenv("ADMIN_PASSWORD", "admin123") # Fallback par défaut

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'login_attempts' not in st.session_state:
    st.session_state['login_attempts'] = 0

def check_password():
    """Vérifie le mot de passe avec protection brute-force."""
    # 1. Délai progressif après 3 échecs
    if st.session_state['login_attempts'] >= 3:
        st.warning("⚠️ Trop de tentatives. Veuillez patienter 30 secondes...")
        time.sleep(30)
        st.session_state['login_attempts'] = 0 # On reset après la punition

    # 2. Vérification
    if st.session_state['username'] == SECURE_USER and st.session_state['password'] == SECURE_PWD:
        st.session_state['authenticated'] = True
        st.session_state['login_attempts'] = 0
    else:
        st.session_state['login_attempts'] += 1
        st.error(f"Identifiant ou mot de passe incorrect (Tentative {st.session_state['login_attempts']}/3)")

def login_page():
    """Affiche la page de connexion centrée."""
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #198754;'><i class='bi bi-shield-lock-fill'></i> MoneyShield CI</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #6c757d;'>Portail d'Administration Sécurisé</h4>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            st.text_input("Identifiant", key="username")
            st.text_input("Mot de passe", type="password", key="password")
            st.form_submit_button("Se connecter", on_click=check_password, type="primary")

if not st.session_state['authenticated']:
    login_page()
else:
    # --- SIDEBAR LOGOUT ---
    st.sidebar.info(f"👤 Connecté : **{SECURE_USER}**")
    if st.sidebar.button("🔒 Déconnexion"):
        st.session_state['authenticated'] = False
        st.rerun()
        
    st.sidebar.markdown("---")

    # --- NAVIGATION EXISTANTE ---
    menu = st.sidebar.radio("Navigation", ["🛡️ Sécurité & Fraude", "💰 Finance & Tendances"])

    if menu == "🛡️ Sécurité & Fraude":
        show_security_dashboard()
    else:
        show_financial_dashboard()

    # --- REFRESH AUTOMATIQUE ---
    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh", value=True, help="Décochez pour mettre en pause le rafraîchissement automatique")

    if auto_refresh:
        time.sleep(5) 
        st.rerun()
    else:
        st.sidebar.warning("⚠️ Refresh en pause")