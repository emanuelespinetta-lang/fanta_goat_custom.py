import pandas as pd
import streamlit as st
import numpy as np
import os

st.set_page_config(page_title="FantaGOAT Custom", layout="wide", initial_sidebar_state="expanded")

# --- 1. TIRATORI E CALCI PIAZZATI ---
RIGORISTI = {
    'Scamacca': 1, 'Krstovic': 2, 'Samardzic': 3, 'Orsolini': 1, 'Bernardeschi': 2, 'Dovbyk': 3,
    'Kevin Carlos': 1, 'Maldini': 2, 'Mina': 3, 'Da Cunha': 1, 'Douvikas': 2, 'Paz N.': 3,
    'Gudmundsson A.': 1, 'Mandragora': 2, 'Calo': 1, 'Schmid': 2, 'Grillitsch': 3,
    'Colombo': 1, 'Ostigard': 2, 'Vitinha': 3, 'Calhanoglu': 1, 'Zielinski': 2, 'Martinez L.': 3,
    'Kolo Muani': 1, 'Yildiz': 2, 'Locatelli': 3, 'Zaccagni': 1, 'Taylor K.': 2, 'Cataldi': 3,
    'Geubbels': 1, 'Stulic': 2, 'Berisha M.': 3, 'Ramos G.': 1, 'Pulisic': 2, 'Modric': 3,
    'Pessina': 1, 'Cutrone': 2, 'Petagna': 3, 'De Bruyne': 1, 'Hojlund': 2, 'Politano': 3,
    'Pellegrino M.': 1, 'Toure E.': 2, 'Valeri': 3, 'Bernabe': 4, 'Malen': 1, 'Dybala': 2, 'Castro S.': 3,
    'Berardi': 1, 'Pinamonti': 2, 'Lauriente': 3, 'Vlasic': 1, 'Kulenovic': 2, 'Simeone': 3
}

PIAZZATI = {
    'De Ketelaere': 1, 'Samardzic': 2, 'Gaetano': 3, 'Orsolini': 1, 'Bernardeschi': 2, 'Miranda J.': 3,
    'Fazzini': 1, 'Maldini': 2, 'Romano': 3, 'Paz N.': 1, 'Baturina': 2, 'Milla': 3,
    'Gudmundsson A.': 1, 'Mastantuono': 2, 'Atta': 3, 'Calo': 1, 'Schmid': 2, 'Ghedjemis': 3,
    'Baldanzi': 1, 'Martin': 2, 'Vitinha O.': 3, 'Calhanoglu': 1, 'Dimarco': 2, 'Zielinski': 3,
    'Yildiz': 1, 'Locatelli': 2, 'Cambiaso': 3, 'Rovella': 1, 'Zaccagni': 2, 'Cataldi': 3,
    'Pierotti': 1, 'Berisha M.': 2, 'Gandelman': 3, 'Modric': 1, 'Pulisic': 2, 'Saelemaekers': 3,
    'Pessina': 1, 'Colpani': 2, 'Mota': 3, 'De Bruyne': 1, 'Politano': 2, 'Neres': 3,
    'Bernabe': 1, 'Nicolussi Caviglia': 2, 'Valeri': 3, 'Dybala': 1, 'Malen': 2, 'Pellegrini Lo.': 3,
    'Berardi': 1, 'Lauriente': 2, 'Adzic': 3, 'Vlasic': 1, 'Oristanio': 2
}

def trova_file(nome_target):
    for root, _, files in os.walk('.'):
        for f in files:
            if f.lower() == nome_target.lower():
                return os.path.join(root, f)
    return None

@st.cache_data
def carica_master_dataset():
    f_stat27 = trova_file("Statistiche_Fantacalcio_Stagione_2026_27_Statistico.xlsx")
    f_stat26 = trova_file("Statistiche_Fantacalcio_Stagione_2025_26_Statistico.xlsx")
    f_quot27 = trova_file("Quotazioni_Fantacalcio_Stagione_2026_27.xlsx")
    
    def pulisci_df(path):
        if not path or not os.path.exists(path):
            return pd.DataFrame()
        d = pd.read_excel(path, header=1)
        d.columns = d.columns.str.strip()
        if 'Nome' in d.columns:
            d['Nome'] = d['Nome'].astype(str).str.strip()
        for c in ['Pv', 'Mv', 'Fm', 'Gf', 'Ass', 'Gs', 'Rp', 'Rc', 'Qt. A', 'Qt. I', 'FVM']:
            if c in d.columns:
                if d[c].dtype == object:
                    d[c] = d[c].astype(str).str.replace(',', '.')
                d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0.0)
        return d

    df27 = pulisci_df(f_stat27)
    df26 = pulisci_df(f_stat26)
    df_q = pulisci_df(f_quot27)

    if df27.empty:
        st.error("❌ File 2026/27 non trovato.")
        st.stop()

    # Mappa statistiche della passata stagione completa (2025/26)
    df26_map = df26.set_index('Nome')[['Fm', 'Mv', 'Pv', 'Gf', 'Ass']].to_dict('index') if not df26.empty else {}
    
    # Mappa FVM / Quotazioni
    fvm_map = {}
    if not df_q.empty and 'Nome' in df_q.columns:
        col_fvm = 'FVM' if 'FVM' in df_q.columns else ('Qt. A' if 'Qt. A' in df_q.columns else 'Qt. I')
        fvm_map = df_q.set_index('Nome')[col_fvm].to_dict()

    df27['Rigorista'] = df27['Nome'].map(RIGORISTI).fillna(0).astype(int)
    df27['Piazzati'] = df27['Nome'].map(PIAZZATI).fillna(0).astype(int)
    df27['FVM_Ufficiale'] = df27['Nome'].map(fvm_map).fillna(1.0)

    # Estrazione statistiche consolidate
    gol_list, ass_list, part_list, perf_list, cont_list = [], [], [], [], []

    for _, row in df27.iterrows():
        nome = row['Nome']
        fvm = row['FVM_Ufficiale']
        d26 = df26_map.get(nome, {'Fm': 0.0, 'Mv': 0.0, 'Pv': 0, 'Gf': 0, 'Ass': 0})
        
        pv = int(d26['Pv']) if d26['Pv'] > 0 else int(row['Pv'])
        gf = int(d26['Gf']) if d26['Pv'] > 0 else int(row['Gf'])
        ass = int(d26['Ass']) if d26['Pv'] > 0 else int(row['Ass'])
        
        gol_list.append(gf)
        ass_list.append(ass)
        part_list.append(pv)

        # Calcolo Continuità (/100)
        if pv >= 30:
            cont = 100
        elif pv > 0:
            cont = max(40, int((pv / 38) * 100))
        else:
            cont = 50 if fvm > 10 else 30
        cont_list.append(cont)

        # Calcolo Performance (/100) calibrato sullo stile FantaGOAT
        # Base su FVM + Bonus ruoli/tiratori
        base_perf = min(95.0, 50.0 + (fvm / 7.0))
        if row['Rigorista'] == 1:
            base_perf += 4.0
        if row['Piazzati'] == 1:
            base_perf += 2.0
        perf_list.append(int(min(99, max(50, round(base_perf)))))

    df27['Tot_Gol'] = gol_list
    df27['Tot_Ass'] = ass_list
    df27['Tot_Part'] = part_list
    df27['Continuita'] = cont_list
    df27['Performance'] = perf_list

    return df27

df_master = carica_master_dataset()

# --- 2. GESTIONE STATO ASTA ---
if 'spesa_totale' not in st.session_state:
    st.session_state.spesa_totale = 0
if 'giocatori_chiamati' not in st.session_state:
    st.session_state.giocatori_chiamati = []

# --- 3. SIDEBAR IMPOSTAZIONI ---
with st.sidebar:
    st.title("⚙️ Pannello Asta")
    partecipanti = st.radio("Partecipanti Lega", [10, 12], index=0)
    budget_iniziale = st.number_input("Budget Singolo Team", value=500, step=50)
    mod_difesa = st.checkbox("Modificatore Difesa", value=False)
    
    st.markdown("---")
    st.subheader("Registra Acquisto")
    giocatori_disponibili = [g for g in df_master['Nome'].unique() if g not in st.session_state.giocatori_chiamati]
    giocatore_selezionato = st.selectbox("Giocatore battuto", ["-"] + sorted(giocatori_disponibili))
    prezzo_effettivo = st.number_input("Prezzo finale pagato", min_value=1, value=1, step=1)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Assegna"):
            if giocatore_selezionato != "-":
                st.session_state.giocatori_chiamati.append(giocatore_selezionato)
                st.session_state.spesa_totale += prezzo_effettivo
                st.rerun()
    with c2:
        if st.button("🔄 Reset Asta"):
            st.session_state.spesa_totale = 0
            st.session_state.giocatori_chiamati = []
            st.rerun()

# --- 4. CALCOLO PREZZI CONSIGLIATI (Budget 500) ---
df_calcolato = df_master.copy()
df_calcolato['Chiamato'] = df_calcolato['Nome'].isin(st.session_state.giocatori_chiamati)

# Rapporto FVM (base 1000) su budget reale (500)
# Se FVM è 300 su 1000 -> vale 150 cr su 500
fattore_scala = budget_iniziale / 1000.0
prezzi = []

for _, r in df_calcolato.iterrows():
    fvm = r['FVM_Ufficiale']
    ruolo = r['R']
    
    # Prezzo base riproporzionato
    pr = fvm * fattore_scala
    
    # Aggiustamenti per tiratori
    if r['Rigorista'] == 1:
        pr *= 1.10
    elif r['Rigorista'] == 2:
        pr *= 1.04
        
    if mod_difesa and ruolo == 'D':
        pr *= 1.15

    prezzi.append(max(1, int(round(pr))))

df_calcolato['Pr_Consig'] = prezzi

# --- 5. INTERFACCIA A SCHEDE (LISTONE / ASTA LIVE) ---
tab_listone, tab_asta = st.tabs(["📋 Listone", "🔨 Asta Live"])

with tab_listone:
    c_search, c_filter, c_order = st.columns([3, 2, 2])
    with c_search:
        cerca = st.text_input("🔍 Cerca giocatore o squadra", placeholder="Es. Martinez L., Roma, Inter...")
    with c_filter:
        filtro_r = st.selectbox("Filtra Ruolo", ["Tutti", "P", "D", "C", "A"])
    with c_order:
        ordina_per = st.selectbox("Ordina per", ["Performance", "Pr. Consig.", "Gol", "Assist", "Partite"])

    col_map = {"Performance": "Performance", "Pr. Consig.": "Pr_Consig", "Gol": "Tot_Gol", "Assist": "Tot_Ass", "Partite": "Tot_Part"}
    
    view_df = df_calcolato[~df_calcolato['Chiamato']].copy()
    if cerca:
        view_df = view_df[view_df['Nome'].str.contains(cerca, case=False, na=False) | view_df['Squadra'].str.contains(cerca, case=False, na=False)]
    if filtro_r != "Tutti":
        view_df = view_df[view_df['R'] == filtro_r]

    view_df = view_df.sort_values(by=col_map[ordina_per], ascending=False)

    colonne_finali = ['Nome', 'Squadra', 'R', 'Pr_Consig', 'Performance', 'Continuita', 'Tot_Gol', 'Tot_Ass', 'Tot_Part']
    st.dataframe(
        view_df[colonne_finali].rename(columns={
            'Pr_Consig': 'Pr. Consig. (cr)',
            'Performance': 'Performance /100',
            'Continuita': 'Continuità /100',
            'Tot_Gol': 'Gol',
            'Tot_Ass': 'Assist',
            'Tot_Part': 'Partite'
        }),
        use_container_width=True,
        hide_index=True
    )

with tab_asta:
    totale_lega = partecipanti * budget_iniziale
    residuo_lega = totale_lega - st.session_state.spesa_totale
    
    colA, colB, colC = st.columns(3)
    colA.metric("Crediti Residui Totali Lega", f"{residuo_lega} cr")
    colB.metric("Crediti Spesi Totali", f"{st.session_state.spesa_totale} cr")
    colC.metric("Giocatori Battuti", f"{len(st.session_state.giocatori_chiamati)}")
    
    st.markdown("---")
    st.subheader("Cronologia Acquisti Registrati")
    if st.session_state.giocatori_chiamati:
        st.write(" • ".join(reversed(st.session_state.giocatori_chiamati[-15:])))
    else:
        st.info("Nessun acquisto ancora registrato.")
