import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Sistema Voto Web", page_icon="🗳️")

# Inizializzazione dello stato della sessione (per non perdere i dati al refresh)
if 'fase' not in st.session_state:
    st.session_state.fase = "configurazione"
if 'punteggi' not in st.session_state:
    st.session_state.punteggi = {}
if 'votanti_rimasti' not in st.session_state:
    st.session_state.votanti_rimasti = 0
if 'voti_totali' not in st.session_state:
    st.session_state.voti_totali = 0

# --- 1. FASE DI CONFIGURAZIONE ---
if st.session_state.fase == "configurazione":
    st.title("🗳️ Configura la Votazione")
    
    proposte_input = st.text_input("Inserisci le proposte separate da virgola:", placeholder="Es: Pizza, Sushi, Hamburger")
    num_persone = st.number_input("Quante persone devono votare?", min_value=1, step=1)
    
    if st.button("Inizia Votazione"):
        if proposte_input:
            lista_p = [p.strip() for p in proposte_input.split(",") if p.strip()]
            st.session_state.punteggi = {p: 0 for p in lista_p}
            st.session_state.votanti_rimasti = num_persone
            st.session_state.voti_totali = num_persone
            st.session_state.fase = "voto"
            st.rerun()
        else:
            st.error("Inserisci almeno una proposta!")

# --- 2. FASE DI VOTO ---
elif st.session_state.fase == "voto":
    st.title("📥 Scheda di Voto")
    st.write(f"Votanti rimasti: **{st.session_state.votanti_rimasti}**")
    
    progress = 1 - (st.session_state.votanti_rimasti / st.session_state.voti_totali)
    st.progress(progress)

    proposte = list(st.session_state.punteggi.keys())
    
    with st.form("form_voto"):
        scelta1 = st.selectbox("1ª Scelta (3 Punti)", ["Seleziona..."] + proposte)
        scelta2 = st.selectbox("2ª Scelta (2 Punti)", ["Seleziona..."] + proposte)
        scelta3 = st.selectbox("3ª Scelta (1 Punto)", ["Seleziona..."] + proposte)
        
        submit = st.form_submit_button("Invia Voto")
        
        if submit:
            scelte = [scelta1, scelta2, scelta3]
            if "Seleziona..." in scelte:
                st.error("Devi compilare tutte e tre le scelte!")
            elif len(set(scelte)) < 3:
                st.error("Non puoi votare la stessa proposta più volte!")
            else:
                # Aggiorna punteggi
                st.session_state.punteggi[scelta1] += 3
                st.session_state.punteggi[scelta2] += 2
                st.session_state.punteggi[scelta3] += 1
                
                st.session_state.votanti_rimasti -= 1
                
                if st.session_state.votanti_rimasti <= 0:
                    st.session_state.fase = "risultati"
                
                st.success("Voto registrato!")
                st.rerun()

# --- 3. FASE RISULTATI ---
elif st.session_state.fase == "risultati":
    st.title("🏆 Classifica Finale")
    
    # Creazione DataFrame per la visualizzazione
    df = pd.DataFrame(
        st.session_state.punteggi.items(), 
        columns=["Proposta", "Punti"]
    ).sort_values(by="Punti", ascending=False)
    
    # Mostra il vincitore con un'evidenza
    vincitore = df.iloc[0]["Proposta"]
    st.balloons()
    st.success(f"La proposta vincitrice è: **{vincitore}**!")
    
    # Tabella e Grafico
    st.table(df.set_index("Proposta"))
    st.bar_chart(df.set_index("Proposta"))
    
    if st.button("Ricomincia Nuova Votazione"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()