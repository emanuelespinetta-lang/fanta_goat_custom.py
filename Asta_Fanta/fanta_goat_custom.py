import pandas as pd
import streamlit as st
import numpy as np
import os

# --- 1. CONFIGURAZIONE E DIZIONARI TIRATORI ---
RIGORISTI = {
    'Scamacca': 1, 'Krstovic': 2, 'Samardzic': 3,
    'Orsolini': 1, 'Bernardeschi': 2, 'Dovbyk': 3,
    'Kevin Carlos': 1, 'Maldini': 2, 'Mina': 3,
    'Da Cunha': 1, 'Douvikas': 2, 'Paz N.': 3,
    'Gudmundsson A.': 1, 'Mandragora': 2,
    'Calo': 1, 'Schmid': 2, 'Grillitsch': 3,
    'Colombo': 1, 'Ostigard': 2, 'Vitinha': 3,
    'Calhanoglu': 1, 'Zielinski': 2, 'Martinez L.': 3,
    'Kolo Muani': 1, 'Yildiz': 2, 'Locatelli': 3,
    'Zaccagni': 1, 'Taylor K.': 2, 'Cataldi': 3,
    'Geubbels': 1, 'Stulic': 2, 'Berisha M.': 3,
    'Ramos G.': 1, 'Pulisic': 2, 'Modric': 3,
    'Pessina': 1, 'Cutrone': 2, 'Petagna': 3,
    'De Bruyne': 1, 'Hojlund': 2, 'Politano': 3,
    'Pellegrino M.': 1, 'Toure E.': 2, 'Valeri': 3, 'Bernabe': 4,
    'Malen': 1, 'Dybala': 2, 'Castro S.': 3,
    'Berardi': 1, 'Pinamonti': 2, 'Lauriente': 3,
    'Vlasic': 1, 'Kulenovic': 2, 'Simeone': 3
}

PIAZZATI = {
    'De Ketelaere': 1, 'Samardzic': 2, 'Gaetano': 3,
    'Orsolini': 1, 'Bernardeschi': 2, 'Miranda J.': 3,
    'Fazzini': 1, 'Maldini': 2, 'Romano': 3,
    'Paz N.': 1, 'Baturina': 2, 'Milla': 3,
    'Gudmundsson A.': 1, 'Mastantuono': 2, 'Atta': 3,
    'Calo': 1, 'Schmid': 2, 'Ghedjemis': 3,
    'Baldanzi': 1, 'Martin': 2, 'Vitinha O.': 3,
    'Calhanoglu': 1, 'Dimarco': 2, 'Zielinski': 3,
    'Yildiz': 1, 'Locatelli': 2, 'Cambiaso': 3,
    'Rovella': 1, 'Zaccagni': 2, 'Cataldi': 3,
    'Pierotti': 1, 'Berisha M.': 2, 'Gandelman': 3,
    'Modric': 1, 'Pulisic': 2, 'Saelemaekers': 3,
    'Pessina': 1, 'Colpani': 2, 'Mota': 3,
    'De Bruyne': 1, 'Politano': 2, 'Neres': 3,
    'Bernabe': 1, 'Nicolussi Caviglia': 2, 'Valeri': 3,
    'Dybala': 1, 'Malen': 2, 'Pellegrini Lo.': 3,
    'Berardi': 1, 'Lauriente': 2, 'Adzic': 3,
    'Vlasic': 1, 'Oristanio': 2
}

@st.cache_data
def carica_dati():
    nome_file = "Statistiche_Fantacalcio_Stagione_2026_27_Statistico.xlsx"
    percorso_esatto = None
    
    # Il radar: cerca il file ovunque nel progetto
    for root, dirs, files in os.walk('.'):
        if nome_file in files:
            percorso_esatto = os.path.join(root, nome_file)
            break
            
    if percorso_esatto is None:
        st.error(f"❌ ERRORE: Non trovo il file '{nome_file}'. Controlla su GitHub di averlo caricato con questo nome esatto (maiuscole comprese).")
        st.stop()
        
    df = pd.read_excel(percorso_esatto)
    
    if df.columns[0] == 'Statistiche Fantacalcio Stagione 2026 27':
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
    
    cols_to_numeric = ['Pv', 'Mv', 'Fm', 'Gf', 'Ass']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    df['Rigorista'] = df['Nome'].map(RIGORISTI).fillna(0)
    df['Piazzati'] = df['Nome'].map(PIAZZATI).fillna(0)
    
    df['GOAT_Score'] = df['Fm'] + np.where(df['Rigorista'] == 1, 0.4, np.where(df['Rigorista'] == 2, 0.15, 0))
    df['GOAT_Score'] = df['GOAT_Score'] + np.where(df['Piazzati'] == 1, 0.2, 0)
    
    return df

# --- 2. INTERFACCIA STREAMLIT E LOGICA D'ASTA ---
st.set_page_config(page_title="Custom FantaGOAT", layout="wide")
st.title("🐐 FantaGOAT Custom Dashboard")

st.sidebar.header("Impostazioni Lega")
partecipanti = st.sidebar.radio("Partecipanti", [10, 12], index=0)
budget_iniziale = st.sidebar.number_input("Budget Iniziale", value=500)
mod_difesa = st.sidebar.checkbox("Modificatore Difesa", value=False)

df_stats = carica_dati()

if 'spesa_totale_lega' not in st.session_state:
    st.session_state.spesa_totale_lega = 0

st.sidebar.markdown("---")
spesa_inserita = st.sidebar.number_input("Inserisci acquisto live (Crediti)", min_value=0, value=0, step=1)
if st.sidebar.button("Registra Acquisto"):
    st.session_state.spesa_totale_lega += spesa_inserita

budget_lega_totale = partecipanti * budget_iniziale
budget_residuo_lega = budget_lega_totale - st.session_state.spesa_totale_lega

st.metric(label="Budget Residuo Globale Lega", value=f"{budget_residuo_lega} cr")

budget_pct = {'P': 0.08, 'D': 0.10, 'C': 0.22, 'A': 0.60}
if mod_difesa:
    budget_pct = {'P': 0.08, 'D': 0.18, 'C': 0.19, 'A': 0.55}

df_stats['Prezzo_Base'] = 1
df_stats['Prezzo_Consigliato_Max'] = 1

for ruolo in ['P', 'D', 'C', 'A']:
    mask = df_stats['R'] == ruolo
    somma_goat = df_stats.loc[mask, 'GOAT_Score'].sum()
    if somma_goat > 0:
        budget_reparto = budget_residuo_lega * budget_pct[ruolo]
        df_stats.loc[mask, 'Prezzo_Consigliato_Max'] = (df_stats.loc[mask, 'GOAT_Score'] / somma_goat) * budget_reparto

df_stats['Prezzo_Consigliato_Max'] = df_stats['Prezzo_Consigliato_Max'].apply(lambda x: max(1, int(x)))

ruolo_scelto = st.selectbox("Filtra per Ruolo", ["Tutti", "P", "D", "C", "A"])
if ruolo_scelto != "Tutti":
    df_mostra = df_stats[df_stats['R'] == ruolo_scelto]
else:
    df_mostra = df_stats

st.dataframe(
    df_mostra[['Nome', 'Squadra', 'R', 'Mv', 'Fm', 'GOAT_Score', 'Rigorista', 'Prezzo_Consigliato_Max']]
    .sort_values(by='Prezzo_Consigliato_Max', ascending=False)
    .head(50), 
    use_container_width=True
)
