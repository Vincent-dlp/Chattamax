import json
from google.oauth2.service_account import Credentials
import gspread

# Charger les informations depuis les secrets Streamlit
import streamlit as st

keyfile_dict = json.loads(st.secrets["GOOGLE_KEY"])
credentials = Credentials.from_service_account_info(keyfile_dict)

# Connexion à Google Sheets
client = gspread.authorize(credentials)

# Ouvrir le fichier Google Sheets
sheet = client.open("Chattamax").sheet1


# Titre de l'application
st.title("Chattamax")

# Formulaire
q1 = st.radio("Qui a pris le bet ?", ["Jo", "Ceba", "Ju","Cardo","Vincent"])
q2 = st.selectbox("Quel sport ?", ["Football", "Tennis", "Ski", "Basket"])
q3 = st.text_input("Intitulé du pari ?")
q4 = st.number_input("Quelle mise ?", min_value=0, step=1, format="%d")
q5 = st.number_input("Quelle cote ? ", min_value=0.0, step=0.05, format="%.2f")

# Bouton pour soumettre
if st.button("Soumettre"):
    # Ajouter les réponses dans Google Sheets
    sheet.append_row([q1, q2, q3, q4, q5])
    st.success("Vos réponses ont été enregistrées avec succès !")
