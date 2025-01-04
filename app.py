import json
from google.oauth2.service_account import Credentials
import gspread

# Charger les informations depuis les secrets Streamlit
import streamlit as st

keyfile_dict = json.loads(st.secrets["GOOGLE_KEY"])
credentials = Credentials.from_service_account_info(keyfile_dict, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])

# Connexion à Google Sheets
client = gspread.authorize(credentials)

# Ouvrir le fichier Google Sheets
sheet = client.open("Chattamax").sheet1

# Titre de l'application
st.title("Chattamax")

# Formulaire
q1 = st.radio("Qui a pris le bet ?", ["Jo", "Ceba", "Ju","Cardo","Vincent"])
q2 = st.selectbox("Quel sport ?", ["Basket","Biathlon","Football","Formule 1","Rugby à 7", "Rugby à 13","Rugby à 15","Ski alpin","Ski de fond", "Tennis"])
q2 = st.selectbox("Quel bet type ?", ["Buteur","Passeur","Ace","Vainqueur","Podium", "H2H","3way","2way", "Buteur et son équipe gagne","Autre"])
q4 = st.text_input("Intitulé du pari ?")
q5 = st.number_input("Quelle mise ?", min_value=0, step=1, format="%d")
q6 = st.number_input("Quelle cote ? ", min_value=0.0, step=0.05, format="%.2f")
q7 = st.radio("Statut du pari ?",["En cours", "Gagnant", "Perdant","Annulé"])

# Bouton pour soumettre
if st.button("Soumettre"):
    # Ajouter les réponses dans Google Sheets
    sheet.append_row([q1, q2, q3, q4, q5])
    st.success("Vos réponses ont été enregistrées avec succès !")
