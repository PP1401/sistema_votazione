import streamlit as st
import pandas as pd

# 1. Configurazione Pagina
st.set_page_config(page_title="Votazione Live Protetta", page_icon="🌐", layout="centered")

@st.cache_resource
def get_global_data():
    # Oggetto condiviso tra tutti i dispositivi
    return {
        "punteggi": {}, 
        "password": "", 
        "votanti_effettivi": 0
    }

data = get_global_data()

st.title("🗳️ Sistema di Voto Globale")

# --- A. AREA CONFIGURAZIONE (ADMIN) ---
if not data["password"]:
    st.info("In attesa della configurazione dell'Amministratore...")
    with st.expander("⚙️ Setup Amministratore"):
        pwd_admin = st.text_input("Imposta Password di Accesso:", type="password")
        prop_admin = st.text_area("Proposte (una per riga o separate da virgola):")
        if st.button("Avvia Sessione"):
            if pwd_admin and prop_admin:
                lista = [p.strip() for p in prop_admin.replace('\n', ',').split(',') if p.strip()]
                data["punteggi"] = {p: 0 for p in lista}
                data["password"] = pwd_admin
                st.rerun()

# --- B. INTERFACCIA UTENTE ---
else:
    with st.sidebar:
        st.header("Autenticazione")
        pass_inserita = st.text_input("Password Votazione:", type="password")
        if st.button("Termina Sessione (Admin)"):
            st.cache_resource.clear()
            st.rerun()
        
    if pass_inserita == data["password"]:
        
        # LOGICA: Se NON ha votato, mostra la scheda
        if not st.session_state.get("ha_votato", False):
            st.subheader("📝 La tua Scheda di Voto")
            st.info("La classifica sarà visibile solo dopo aver confermato il tuo voto.")
            
            with st.form("form_voto"):
                opzioni = sorted(list(data["punteggi"].keys()))
                c1 = st.selectbox("🥇 1ª Scelta (3 pt)", ["-"] + opzioni)
                c2 = st.selectbox("🥈 2ª Scelta (2 pt)", ["-"] + opzioni)
                c3 = st.selectbox("🥉 3ª Scelta (1 pt)", ["-"] + opzioni)
                
                if st.form_submit_button("Conferma ed Invia"):
                    scelte = [c1, c2, c3]
                    if "-" in scelte or len(set(scelte)) < 3:
                        st.error("Seleziona 3 opzioni diverse.")
                    else:
                        # Aggiornamento dati globali
                        data["punteggi"][c1] += 3
                        data["punteggi"][c2] += 2
                        data["punteggi"][c3] += 1
                        data["votanti_effettivi"] += 1
                        
                        # Segna l'utente come "votante" per questa sessione
                        st.session_state["ha_votato"] = True
                        st.balloons()
                        st.rerun()
        
        # LOGICA: Se HA votato, mostra la classifica
        else:
            st.success("✅ Grazie! Il tuo voto è stato registrato.")
            st.divider()
            st.subheader("📊 Classifica Live")
            st.write(f"Votanti totali: **{data['votanti_effettivi']}**")
            
            # Preparazione Classifica
            df = pd.DataFrame(data["punteggi"].items(), columns=["Opzione", "Punti"])
            df = df.sort_values(by="Punti", ascending=False).reset_index(drop=True)
            
            # Visualizzazione con barre di progresso
            for i, row in df.iterrows():
                col_name, col_pts = st.columns([3, 1])
                col_name.write(f"**{i+1}° {row['Opzione']}**")
                col_pts.write(f"{row['Punti']} pt")
                # Calcola percentuale per la barra (massimo teorico dei punti per una singola opzione)
                max_teorico = max(df["Punti"].max(), 1)
                st.progress(row["Punti"] / max_teorico)
            
            if st.button("🔄 Aggiorna Risultati"):
                st.rerun()

    elif pass_inserita != "":
        st.error("Password errata.")
    else:
        st.warning("Inserisci la password nella barra laterale per partecipare.")
