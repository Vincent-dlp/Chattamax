import streamlit as st

# Titre de l'application
st.title("Chattamax")

# Exemple d'une question simple
q1 = st.radio("Qui a placé le bet", ["Jo", "Céba", "Ju","Cardo","Vincent"])
q2 = st.text_input("Intitulé du pari")

if st.button("Soumettre"):
    st.write("Merci pour vos réponses !")
