import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuration API
API_KEY = "8610d983bdbd1a47d730f42a0f595b7f"  # Remplacez par votre clé API Football
BASE_URL = "https://v3.football.api-sports.io/"
HEADERS = {"x-apisports-key": API_KEY}

# Liste des ligues disponibles
LEAGUES = {
    129: "Primera Nacional (Argentina)",
    188: "A-League (Australia)",
    344: "Primera División (Bolivia)",
    71: "Serie A (Brazil)",
    265: "Primera División (Chile)",
    169: "Super League (China)",
    239: "Primera A (Colombia)",
    242: "Liga Pro (Ecuador)",
    98: "J1 League (Japan)",
    262: "Liga MX (Mexico)",
    250: "Division Profesional - Apertura (Paraguay)",
    252: "Division Profesional - Clausura (Paraguay)",
    307: "Pro League (Saudi-Arabia)",
    253: "Major League Soccer (USA)"
}

SEASONS = [2024, 2025]  # Saisons disponibles

# Interface utilisateur avec Streamlit
st.title("⚽ Analyse des Statistiques de Football")
st.sidebar.header("📊 Filtres")

# Sélection des ligues
selected_leagues = st.sidebar.multiselect("Sélectionnez les ligues à analyser", options=list(LEAGUES.keys()), format_func=lambda x: LEAGUES[x])

# Paramètres de filtrage
min_goals = st.sidebar.slider("Nombre minimum de buts", 0, 10, 2)
min_assists = st.sidebar.slider("Nombre minimum de passes décisives", 0, 10, 2)

# Bouton de lancement
if st.sidebar.button("Lancer l'analyse"):
    st.write("🔄 Analyse en cours...")
    
    team_ids = {}
    
    # Récupérer les équipes des ligues sélectionnées
    for league_id in selected_leagues:
        for season in SEASONS:
            url_teams = f"{BASE_URL}teams?league={league_id}&season={season}"
            response_teams = requests.get(url_teams, headers=HEADERS)
            data_teams = response_teams.json()
            
            if "response" in data_teams and data_teams["response"]:
                for team in data_teams["response"]:
                    team_ids[team["team"]["id"]] = {"nom": team["team"]["name"]}
    
    # Récupérer les 10 derniers matchs des équipes
    all_fixtures = set()
    for team_id in team_ids.keys():
        for season in SEASONS:
            url_fixtures = f"{BASE_URL}fixtures?team={team_id}&season={season}"
            response_fixtures = requests.get(url_fixtures, headers=HEADERS)
            data_fixtures = response_fixtures.json()
            
            if "response" in data_fixtures:
                matches = sorted(
                    [match for match in data_fixtures.get("response", []) 
                     if match['league']['id'] in selected_leagues and match['fixture']['status']['short'] == "FT"],
                    key=lambda x: x['fixture']['date'], reverse=True
                )[:10]  # Prendre les 10 derniers matchs
                
                all_fixtures.update(match['fixture']['id'] for match in matches)
    
    # Récupérer les stats des joueurs
    players_stats = {}
    for fixture_id in all_fixtures:
        url_players_stats = f"{BASE_URL}fixtures/players?fixture={fixture_id}"
        response_players_stats = requests.get(url_players_stats, headers=HEADERS)
        data_players_stats = response_players_stats.json()
        
        if "response" in data_players_stats:
            for team_data in data_players_stats["response"]:
                team_id = team_data['team']['id']
                team_name = team_ids.get(team_id, {}).get("nom", "Inconnu")
                
                for player_data in team_data["players"]:
                    if player_data.get("statistics"):
                        player_id = player_data["player"]["id"]
                        player_name = player_data["player"]["name"]
                        goals = player_data["statistics"][0]["goals"].get("total", 0) or 0
                        assists = player_data["statistics"][0]["goals"].get("assists", 0) or 0
                        minutes_played = player_data["statistics"][0]["games"].get("minutes", 0) or 0
                        matches_played = 1 if minutes_played > 1 else 0
                        
                        if player_id not in players_stats:
                            players_stats[player_id] = {"Nom": player_name, "Club": team_name, "Buts": 0, "Passes D": 0, "Matchs Joués": 0, "Minutes Jouées": 0, "Temps de jeu moyen": 0, "Buts toutes les X minutes": 0}
                        
                        players_stats[player_id]["Buts"] += goals
                        players_stats[player_id]["Passes D"] += assists
                        players_stats[player_id]["Matchs Joués"] += matches_played
                        players_stats[player_id]["Minutes Jouées"] += minutes_played
                        players_stats[player_id]["Temps de jeu moyen"] = players_stats[player_id]["Minutes Jouées"] / max(players_stats[player_id]["Matchs Joués"], 1)
                        players_stats[player_id]["Buts toutes les X minutes"] = players_stats[player_id]["Minutes Jouées"] / max(players_stats[player_id]["Buts"], 1)
    
    # Filtrer les joueurs selon les critères définis
    filtered_players = [
        stats for stats in players_stats.values()
        if stats['Buts'] >= min_goals or stats['Passes D'] >= min_assists
    ]
    
    # Convertir les résultats en DataFrame
    df_results = pd.DataFrame(filtered_players)
    
    if not df_results.empty:
        st.write("### Résultats de l'analyse")
        st.dataframe(df_results.sort_values(by="Buts", ascending=False))
    else:
        st.write("❌ Aucun joueur ne correspond aux critères sélectionnés.")
