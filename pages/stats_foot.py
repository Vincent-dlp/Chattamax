import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuration API
API_KEY = "VOTRE_CLE_API"  # Remplacez par ta clé API Football
BASE_URL = "https://v3.football.api-sports.io/"
HEADERS = {"x-apisports-key": API_KEY}

# Liste des ligues disponibles
LEAGUES = {
    129: "Primera Nacional (Argentine)",
    188: "A-League (Australie)",
    344: "Super League (Chine)",
    71: "Serie A (Brésil)",
    265: "Major League Soccer (USA)",
    169: "Liga MX (Mexique)",
    239: "Ekstraklasa (Pologne)",
    242: "Allsvenskan (Suède)",
    98: "J1 League (Japon)",
    262: "K League 1 (Corée du Sud)",
    250: "Super League (Suisse)",
    252: "Eliteserien (Norvège)",
    307: "Premier League (Afrique du Sud)",
    253: "Liga 1 (Indonésie)"
}

SEASONS = [2024, 2025]  # Saisons disponibles

# Interface utilisateur avec Streamlit
st.title("⚽ Analyse des Statistiques de Football")
st.sidebar.header("📊 Filtres")

# Sélection des ligues
selected_leagues = st.sidebar.multiselect("Sélectionnez les ligues à analyser", options=list(LEAGUES.keys()), format_func=lambda x: LEAGUES[x])

# Paramètres de filtrage
min_matches = st.sidebar.slider("Nombre minimum de matchs joués par le joueur", 1, 10, 3)
min_goals = st.sidebar.slider("Nombre minimum de buts", 0, 10, 2)
min_assists = st.sidebar.slider("Nombre minimum de passes décisives", 0, 10, 2)

# Bouton de lancement
if st.sidebar.button("Lancer l'analyse"):
    st.write("🔄 Analyse en cours...")
    
    team_ids = {}
    league_mapping = {}
    
    # Récupérer les équipes des ligues sélectionnées
    for league_id in selected_leagues:
        for season in SEASONS:
            url_teams = f"{BASE_URL}teams?league={league_id}&season={season}"
            response_teams = requests.get(url_teams, headers=HEADERS)
            data_teams = response_teams.json()
            
            if "response" in data_teams and data_teams["response"]:
                for team in data_teams["response"]:
                    team_ids[team["team"]["id"]] = {"nom": team["team"]["name"], "ligue": league_id}
                    league_mapping[team["team"]["id"]] = league_id
    
    # Récupérer les stats des joueurs
    players_stats = {}
    for team_id in team_ids.keys():
        for season in SEASONS:
            url_players = f"{BASE_URL}players?team={team_id}&season={season}"
            response_players = requests.get(url_players, headers=HEADERS)
            data_players = response_players.json()
            
            if "response" in data_players:
                for player_data in data_players["response"]:
                    player_id = player_data["player"]["id"]
                    player_name = player_data["player"]["name"]
                    team_name = team_ids.get(team_id, {}).get("nom", "Inconnu")
                    goals = player_data["statistics"][0]["goals"].get("total", 0) or 0
                    assists = player_data["statistics"][0]["goals"].get("assists", 0) or 0
                    matches_played = player_data["statistics"][0]["games"].get("appearences", 0) or 0
                    minutes_played = player_data["statistics"][0]["games"].get("minutes", 0) or 0
                    avg_minutes = minutes_played / matches_played if matches_played > 0 else 0
                    goals_per_minute = minutes_played / goals if goals > 0 else 0
                    
                    if player_id not in players_stats:
                        players_stats[player_id] = {
                            "Nom": player_name,
                            "Club": team_name,
                            "Buts": goals,
                            "Passes D": assists,
                            "Matchs Joués": matches_played,
                            "Minutes Jouées": minutes_played,
                            "Moyenne Minutes": avg_minutes,
                            "Buts toutes les X min": goals_per_minute
                        }
    
    # Filtrer les joueurs
    filtered_players = [player for player in players_stats.values() if player["Buts"] >= min_goals or player["Passes D"] >= min_assists and player["Matchs Joués"] >= min_matches]
    
    df_results = pd.DataFrame(filtered_players)
    
    if not df_results.empty:
        st.write("### Résultats de l'analyse")
        st.dataframe(df_results.sort_values(by="Buts", ascending=False))
    else:
        st.write("❌ Aucun joueur ne correspond aux critères sélectionnés.")
