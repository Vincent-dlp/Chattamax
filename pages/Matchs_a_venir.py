import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuration API
API_KEY = "8610d983bdbd1a47d730f42a0f595b7f"  # Remplacez par votre clé API Football
BASE_URL = "https://v3.football.api-sports.io/"
HEADERS = {"x-apisports-key": API_KEY}

# Ligues sélectionnées
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
    253: "Major League Soccer (USA)",
    310: "Superliga (Albania)",
    218: "Bundesliga (Austria)",
    144: "Jupiler Pro League (Belgium)",
    172: "First League (Bulgaria)",
    345: "Czech Liga (Czech-Republic)",
    119: "Superliga (Denmark)",
    39: "Premier League (England)",
    40: "Championship (England)",
    329: "Meistriliiga (Estonia)",
    244: "Veikkausliiga (Finland)",
    61: "Ligue 1 (France)",
    62: "Ligue 2 (France)",
    327: "Erovnuli Liga (Georgia)",
    78: "Bundesliga (Germany)",
    79: "2. Bundesliga (Germany)",
    197: "Super League 1 (Greece)",
    271: "NB I (Hungary)",
    165: "1. Deild (Iceland)",
    357: "Premier Division (Ireland)",
    383: "Ligat Ha'al (Israel)",
    135: "Serie A (Italy)",
    136: "Serie B (Italy)",
    389: "Premier League (Kazakhstan)",
    364: "1. Liga (Latvia)",
    362: "A Lyga (Lithuania)",
    88: "Eredivisie (Netherlands)",
    408: "Premiership (Northern-Ireland)",
    103: "Eliteserien (Norway)",
    94: "Primeira Liga (Portugal)",
    95: "Segunda Liga (Portugal)",
    283: "Liga I (Romania)",
    235: "Premier League (Russia)",
    179: "Premiership (Scotland)",
    286: "Super Liga (Serbia)",
    332: "Super Liga (Slovakia)",
    140: "La Liga (Spain)",
    141: "Segunda División (Spain)",
    113: "Allsvenskan (Sweden)",
    207: "Super League (Switzerland)",
    203: "Süper Lig (Turkey)",
    333: "Premier League (Ukraine)",
    110: "Premier League (Wales)",
    2: "UEFA Champions League (World)",
    3: "UEFA Europa League (World)",
    848: "UEFA Europa Conference League (World)"
}

# Initialisation de l'état
if "matchs_generes" not in st.session_state:
    st.session_state["matchs_generes"] = False
if "match_selectionne" not in st.session_state:
    st.session_state["match_selectionne"] = False
if "selected_match_id" not in st.session_state:
    st.session_state["selected_match_id"] = None

st.set_page_config(page_title="Matchs à venir", layout="wide")
st.title("📅 Matchs à venir")

# Bouton de génération
if st.button("🎲 Générer les matchs à venir"):
    st.session_state["matchs_generes"] = True
    st.session_state["match_selectionne"] = False

# Fonctions auxiliaires
def get_upcoming_fixtures():
    upcoming_matches = {}
    match_labels = {}
    end_date = datetime.utcnow() + timedelta(hours=72)
    today = datetime.utcnow()
    for league_id, league_name in LEAGUES.items():
        url = f"{BASE_URL}fixtures?league={league_id}&from={today.strftime('%Y-%m-%d')}&to={end_date.strftime('%Y-%m-%d')}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        for match in data.get("response", []):
            fixture_id = match["fixture"]["id"]
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            date = match["fixture"]["date"][:16].replace("T", " ")
            label = f"{home} vs {away} ({league_name}) - {date}"
            upcoming_matches[fixture_id] = match
            match_labels[fixture_id] = label
    return upcoming_matches, match_labels

def get_player_stats(fixtures):
    players_stats = {}
    for fixture_id in fixtures:
        url_players_stats = f"{BASE_URL}fixtures/players?fixture={fixture_id}"
        response_players_stats = requests.get(url_players_stats, headers=HEADERS)
        data_players_stats = response_players_stats.json()
        if "response" in data_players_stats:
            for team_data in data_players_stats["response"]:
                for player_data in team_data["players"]:
                    if player_data.get("statistics"):
                        player_id = player_data["player"]["id"]
                        player_name = player_data["player"]["name"]
                        goals = player_data["statistics"][0]["goals"].get("total", 0) or 0
                        assists = player_data["statistics"][0]["goals"].get("assists", 0) or 0
                        minutes_played = player_data["statistics"][0]["games"].get("minutes", 0) or 0
                        matches_played = 1 if minutes_played > 10 else 0
                        if player_id not in players_stats:
                            players_stats[player_id] = {"Nom": player_name, "Buts": 0, "Passes D": 0, "Matchs Joués": 0, "Minutes Jouées": 0, "Temps de jeu moyen": 0, "Buts toutes les X minutes": 0}
                        players_stats[player_id]["Buts"] += goals
                        players_stats[player_id]["Passes D"] += assists
                        players_stats[player_id]["Matchs Joués"] += matches_played
                        players_stats[player_id]["Minutes Jouées"] += minutes_played
                        players_stats[player_id]["Temps de jeu moyen"] = round(players_stats[player_id]["Minutes Jouées"] / max(players_stats[player_id]["Matchs Joués"], 1))
                        players_stats[player_id]["Buts toutes les X minutes"] = round(players_stats[player_id]["Minutes Jouées"] / max(players_stats[player_id]["Buts"], 1))
    return players_stats

# Affichage après clic sur "Générer les matchs"
if st.session_state["matchs_generes"]:
    upcoming_matches, match_labels = get_upcoming_fixtures()
    match_options = list(upcoming_matches.keys())
    selected_match = st.selectbox("Choisissez un match à analyser", match_options, format_func=lambda x: match_labels[x], key="match_selector")

    if selected_match:
        if st.button("Lancer l'analyse"):
            st.session_state["match_selectionne"] = True
            st.session_state["selected_match_id"] = selected_match

# Affichage des résultats
if st.session_state["match_selectionne"] and st.session_state["selected_match_id"]:
    st.write("🔍 Analyse en cours...")
    match_id = st.session_state["selected_match_id"]
    fixtures = [match_id]
    players_stats = get_player_stats(fixtures)
    filtered_players = [
        stats for stats in players_stats.values()
        if stats['Minutes Jouées'] > 10
    ]
    df_results = pd.DataFrame(filtered_players)
    if not df_results.empty:
        st.write("### Résultats de l'analyse")
        st.dataframe(df_results.sort_values(by="Buts", ascending=False))
    else:
        st.write("❌ Aucun joueur ne correspond aux critères sélectionnés.")
