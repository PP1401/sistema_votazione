import streamlit as st
import pandas as pd

# 1. Configurazione Pagina
st.set_page_config(page_title="Votazione Live", page_icon="🌐", layout="centered")

# Funzione per simulare un database condiviso (in un caso reale useresti st.connection)
# Usiamo l'annotazione @st.cache_resource per far sì che questo oggetto sia lo stesso per TUTTI gli utenti
@st.cache_resource
def get_global_data():
    return {
        "punteggi": {}, 
        "password": "", 
        "votanti_effettivi": 0,
        "voti_registrati": [] # Per evitare che la stessa persona voti due volte (basato su ID sessione)
    }

data = get_global_data()

# CSS per rendere l'interfaccia moderna
st.markdown("""
    <style>
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .voto-card { border: 1px solid #ddd; padding: 20px; border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI ACCESSO ---
st.title("🗳️ Sistema di Voto Globale")

# Se l'admin non ha ancora impostato nulla
if not data["password"]:
    st.info("In attesa che l'Amministratore configuri la sessione...")
    with st.expander("Area Amministratore"):
        pwd_admin = st.text_input("Imposta Password per questa votazione:", type="password")
        prop_admin = st.text_area("Proposte (separate da virgola):")
        if st.button("Avvia Sessione Globale"):
            if pwd_admin and prop_admin:
                lista = [p.strip() for p in prop_admin.split(",") if p.strip()]
                data["punteggi"] = {p: 0 for p in lista}
                data["password"] = pwd_admin
                data["voti_registrati"] = []
                st.rerun()
            else:
                st.error("Inserisci password e proposte!")
else:
    # --- INTERFACCIA UTENTE (VOTO E CLASSIFICA) ---
    
    # Sidebar per Autenticazione
    with st.sidebar:
        st.header("Autenticazione")
        pass_inserita = st.text_input("Inserisci Password Votazione:", type="password")
        
    if pass_inserita == data["password"]:
        st.success("Accesso eseguito! Puoi votare o vedere i risultati.")
        
        # Layout a due colonne: Voto a sinistra, Classifica a destra
        col_voto, col_classifica = st.columns([1, 1])
        
        with col_voto:
            st.subheader("La tua Scheda")
            
            # Controllo se l'utente ha già votato in questa sessione browser
            if st.session_state.get("ha_votato", False):
                st.warning("Hai già inviato il tuo voto in questa sessione.")
            else:
                with st.form("form_voto"):
                    opzioni = sorted(list(data["punteggi"].keys()))
                    c1 = st.selectbox("1ª Scelta (3 pt)", ["-"] + opzioni)
                    c2 = st.selectbox("2ª Scelta (2 pt)", ["-"] + opzioni)
                    c3 = st.selectbox("3ª Scelta (1 pt)", ["-"] + opzioni)
                    
                    if st.form_submit_button("Invia Voto"):
                        scelte = [c1, c2, c3]
                        if "-" in scelte or len(set(scelte)) < 3:
                            st.error("Seleziona 3 opzioni diverse.")
                        else:
                            # Aggiornamento dati GLOBALI
                            data["punteggi"][c1] += 3
                            data["punteggi"][c2] += 2
                            data["punteggi"][c3] += 1
                            data["votanti_effettivi"] += 1
                            st.session_state["ha_votato"] = True
                            st.balloons()
                            st.rerun()

        with col_classifica:
            st.subheader("Classifica Live")
            st.write(f"Voti totali ricevuti: **{data['votanti_effettivi']}**")
            
            # Creazione classifica
            df = pd.DataFrame(data["punteggi"].items(), columns=["Opzione", "Punti"])
            df = df.sort_values(by="Punti", ascending=False)
            
            # Mostra i risultati
            for i, row in df.iterrows():
                st.write(f"**{row['Opzione']}**: {row['Punti']} pt")
                st.progress(min(row['Punti'] / (data['votanti_effettivi'] * 3 + 1), 1.0))
            
            if st.button("Aggiorna Classifica"):
                st.rerun()

    elif pass_inserita != "":
        st.error("Password errata.")
    else:
        st.warning("Inserisci la password nella barra laterale per partecipare.")

# Tasto di Reset (solo per l'Admin, visibile in fondo)
if st.sidebar.button("Termina e Reset Totale"):
    st.cache_resource.clear()
    st.rerun()
