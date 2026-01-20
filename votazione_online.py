import streamlit as st
import pandas as pd

# 1. Configurazione Stile e Layout
st.set_page_config(page_title="Voting System Pro", page_icon="🗳️", layout="centered")

# CSS personalizzato per rendere l'interfaccia più moderna
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #4A90E2; color: white; }
    .voter-card { padding: 20px; border-radius: 10px; border: 1px solid #e6e9ef; background-color: white; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .result-card { padding: 15px; border-left: 5px solid #4A90E2; background-color: white; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 2. Gestione dello Stato
if 'fase' not in st.session_state:
    st.session_state.fase = "config"
if 'punteggi' not in st.session_state:
    st.session_state.punteggi = {}
if 'voti_effettuati' not in st.session_state:
    st.session_state.voti_effettuati = 0
if 'totale_votanti' not in st.session_state:
    st.session_state.totale_votanti = 0

# --- FUNZIONI DI SUPPORTO ---
def reset_gara():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- A. SCHERMATA CONFIGURAZIONE ---
if st.session_state.fase == "config":
    st.title("⚙️ Configurazione")
    with st.container():
        st.markdown('<div class="voter-card">', unsafe_allow_html=True)
        prop_raw = st.text_area("Proposte (una per riga o separate da virgola):", placeholder="Esempio:\nProposta A\nProposta B\nProposta C")
        n_votanti = st.number_input("Numero di persone che voteranno:", min_value=1, value=5)
        
        if st.button("Configura ed Inizia"):
            # Pulizia input: accetta sia virgole che invio
            lista = prop_raw.replace('\n', ',').split(',')
            proposte = [p.strip() for p in lista if p.strip()]
            
            if len(proposte) < 3:
                st.error("Inserisci almeno 3 proposte per i 3 livelli di voto!")
            else:
                st.session_state.punteggi = {p: 0 for p in proposte}
                st.session_state.totale_votanti = n_votanti
                st.session_state.fase = "voto"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- B. SCHERMATA DI VOTO ---
elif st.session_state.fase == "voto":
    st.title(f"🗳️ Sessione di Voto")
    
    # Barra di avanzamento
    progresso = st.session_state.voti_effettuati / st.session_state.totale_votanti
    st.progress(progresso)
    st.write(f"Votante **{st.session_state.voti_effettuati + 1}** di {st.session_state.totale_votanti}")

    st.markdown('<div class="voter-card">', unsafe_allow_html=True)
    with st.form("scheda_voto", clear_on_submit=True):
        st.subheader("La tua preferenza")
        opzioni = sorted(list(st.session_state.punteggi.keys()))
        
        c1 = st.selectbox("🥇 1ª Scelta (3 punti)", ["-"] + opzioni)
        c2 = st.selectbox("🥈 2ª Scelta (2 punti)", ["-"] + opzioni)
        c3 = st.selectbox("🥉 3ª Scelta (1 punto)", ["-"] + opzioni)
        
        if st.form_submit_button("Conferma Scelte"):
            scelte = [c1, c2, c3]
            if "-" in scelte:
                st.error("Seleziona tutte e tre le opzioni.")
            elif len(set(scelte)) < 3:
                st.error("Non puoi votare la stessa proposta più volte.")
            else:
                # Assegnazione punti
                st.session_state.punteggi[c1] += 3
                st.session_state.punteggi[c2] += 2
                st.session_state.punteggi[c3] += 1
                
                st.session_state.voti_effettuati += 1
                
                if st.session_state.voti_effettuati >= st.session_state.totale_votanti:
                    st.session_state.fase = "risultati"
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Avviso Privacy
    st.info("💡 I risultati sono nascosti. Verranno mostrati solo dopo l'ultimo voto.")

# --- C. SCHERMATA RISULTATI ---
elif st.session_state.fase == "risultati":
    st.title("📊 Risultati Finali")
    st.balloons()
    
    # Elaborazione dati
    df = pd.DataFrame(st.session_state.punteggi.items(), columns=["Proposta", "Punti"])
    df = df.sort_values(by="Punti", ascending=False).reset_index(drop=True)
    
    # Podio Visivo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏆 Vincitore", df.iloc[0]["Proposta"], f"{df.iloc[0]['Punti']} pt")
    with col2:
        if len(df) > 1: st.metric("🥈 2° Posto", df.iloc[1]["Proposta"], f"{df.iloc[1]['Punti']} pt")
    with col3:
        if len(df) > 2: st.metric("🥉 3° Posto", df.iloc[2]["Proposta"], f"{df.iloc[2]['Punti']} pt")

    st.write("---")
    
    # Classifica dettagliata con card
    for i, row in df.iterrows():
        st.markdown(f"""
            <div class="result-card">
                <span style="font-weight:bold; color:#4A90E2;">{i+1}° Posto:</span> 
                {row['Proposta']} — <strong>{row['Punti']} Punti</strong>
            </div>
            """, unsafe_allow_html=True)

    # Grafico
    st.subheader("Distribuzione Voti")
    st.bar_chart(df.set_index("Proposta"))

    if st.button("Nuova Votazione"):
        reset_gara()
