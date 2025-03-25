import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuration API
API_KEY = "8610d983bdbd1a47d730f42a0f595b7f"  # Remplacez par votre clé API Football
BASE_URL = "https://v3.football.api-sports.io/"
HEADERS = {"x-apisports-key": API_KEY}

# Liste des ligues concernées
LEAGUES = [
    129, 188, 344, 71, 265, 169, 239, 242, 98, 262, 250, 252,
    307, 253, 310, 218, 144, 172, 345, 119, 39, 40, 329, 244,
    61, 62, 327, 78, 79, 197, 271, 165, 357, 383, 135, 136,
    389, 364, 362, 88, 408, 103, 94, 95, 283, 235, 179, 286,
    332, 140, 141, 113, 207, 203, 333, 110, 2, 3, 848
]

SEASONS = [2024, 2025]

st.set_page_config(page_title="Matchs à venir", layout="wide")
st.title("📅 Matchs à venir")

@st.cache_data(show_spinner=False)
def get_upcoming_matches():
    matches = []
    now = datetime.utcnow()
    end_time = now + timedelta(hours=72)
    now_str = now.strftime("%Y-%m-%d")
    end_str = end_time.strftime("%Y-%m-%d")

    for league_id in LEAGUES:
        for season in SEASONS:
            url = f"{BASE_URL}fixtures?league={league_id}&season={season}&from={now_str}&to={end_str}"
            response = requests.get(url, headers=HEADERS)
            data = response.json()
            for match in data.get("response", []):
                fixture_id = match['fixture']['id']
                home = match['teams']['home']['name']
                away = match['teams']['away']['name']
                date = match['fixture']['date'][:16].replace("T", " ")
                matches.append({
                    "id": fixture_id,
                    "label": f"{home} vs {away} ({date})"
                })
    return matches

@st.cache_data(show_spinner=False)
def get_fixture_player_stats(fixture_ids):
    players_stats = {}
    for fixture_id in fixture_ids:
        url = f"{BASE_URL}fixtures/players?fixture={fixture_id}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        for team_data in data.get("response", []):
            for player_data in team_data.get("players", []):
                if player_data.get("statistics"):
                    stats = player_data["statistics"][0]
                    player_id = player_data["player"]["id"]
                    name = player_data["player"]["name"]
                    goals = stats["goals"].get("total", 0) or 0
                    assists = stats["goals"].get("assists", 0) or 0
                    minutes = stats["games"].get("minutes", 0) or 0
                    matches = 1 if minutes > 0 else 0

                    if player_id not in players_stats:
                        players_stats[player_id] = {
                            "Nom": name,
                            "Buts": 0,
                            "Passes D": 0,
                            "Matchs Joués": 0,
                            "Minutes Jouées": 0,
                            "Temps de jeu moyen": 0,
                            "Buts toutes les X minutes": 0,
                        }
                    players_stats[player_id]["Buts"] += goals
                    players_stats[player_id]["Passes D"] += assists
                    players_stats[player_id]["Matchs Joués"] += matches
                    players_stats[player_id]["Minutes Jouées"] += minutes
                    players_stats[player_id]["Temps de jeu moyen"] = round(players_stats[player_id]["Minutes Jouées"] / max(players_stats[player_id]["Matchs Joués"], 1))
                    players_stats[player_id]["Buts toutes les X minutes"] = round(players_stats[player_id]["Minutes Jouées"] / max(players_stats[player_id]["Buts"], 1))

    return list(players_stats.values())

if st.button("🎯 Générer les matchs à venir"):
    all_matches = get_upcoming_matches()
    if not all_matches:
        st.warning("Aucun match à venir trouvé pour les 72 prochaines heures.")
    else:
        match_dict = {m["label"]: m["id"] for m in all_matches}
        selected_label = st.selectbox("Sélectionnez un match à analyser", options=list(match_dict.keys()))

        if st.button("Lancer l'analyse"):
            st.write("🔎 Analyse en cours...")
            selected_id = match_dict[selected_label]

            # Récupérer les deux équipes du match
            url_match = f"{BASE_URL}fixtures?id={selected_id}"
            match_data = requests.get(url_match, headers=HEADERS).json()

            team_ids = []
            for item in match_data.get("response", []):
                team_ids.append(item['teams']['home']['id'])
                team_ids.append(item['teams']['away']['id'])

            # Récupérer les matchs des 3 derniers mois
            start_date = (datetime.utcnow() - timedelta(days=90)).strftime('%Y-%m-%d')
            end_date = datetime.utcnow().strftime('%Y-%m-%d')

            all_fixture_ids = []
            for team_id in team_ids:
                for season in SEASONS:
                    url_fixtures = f"{BASE_URL}fixtures?team={team_id}&season={season}&from={start_date}&to={end_date}"
                    response = requests.get(url_fixtures, headers=HEADERS)
                    data = response.json()
                    fixture_ids = [m['fixture']['id'] for m in data.get("response", []) if m['fixture']['status']['short'] == "FT"]
                    all_fixture_ids.extend(fixture_ids)

            # Récup stats joueurs
            stats = get_fixture_player_stats(all_fixture_ids)
            df_results = pd.DataFrame(stats)

            if not df_results.empty:
                st.write("### Résultats de l'analyse")
                st.dataframe(df_results.sort_values(by="Buts", ascending=False))
            else:
                st.write("❌ Aucun joueur ne correspond aux critères.")
