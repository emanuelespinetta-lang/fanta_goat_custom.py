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

@st.cache_data(ttl=60)
def carica_master_dataset():
    f_stat27 = trova_file("Statistiche_Fantacalcio_Stagione_2026_27_Statistico.xlsx")
    f_stat26 = trova_file("Statistiche_Fantacalcio_Stagione_2025_26_Statistico.xlsx")
    f_quot27 = trova_file("Quotazioni_Fantacalcio_Stagione_2026_27.xlsx")
    
    df27 = pulisci_df(f_stat27)
    df26 = pulisci_df(f_stat26)
    df_q = pulisci_df(f_quot27)

    if df27.empty:
        st.error("❌ File 2026/27 non trovato.")
        st.stop()

    # Mappa ESCLUSIVA delle statistiche dell'anno scorso (2025/26)
    df26_map = df26.set_index('Nome')[['Fm', 'Mv', 'Pv', 'Gf', 'Ass']].to_dict('index') if not df26.empty else {}
    
    # Mappa FVM
    fvm_map = {}
    if not df_q.empty and 'Nome' in df_q.columns:
        col_fvm = 'FVM' if 'FVM' in df_q.columns else ('Qt. A' if 'Qt. A' in df_q.columns else 'Qt. I')
        fvm_map = df_q.set_index('Nome')[col_fvm].to_dict()

    df27['Rigorista'] = df27['Nome'].map(RIGORISTI).fillna(0).astype(int)
    df27['Piazzati'] = df27['Nome'].map(PIAZZATI).fillna(0).astype(int)
    df27['FVM_Ufficiale'] = df27['Nome'].map(fvm_map).fillna(1.0)

    gol_scorso_anno, ass_scorso_anno, part_scorso_anno = [], [], []
    perf_list, cont_list = [], []

    for _, row in df27.iterrows():
        nome = row['Nome']
        fvm = row['FVM_Ufficiale']
        
        # DATI MOSTRATI: SOLO ED ESCLUSIVAMENTE 2025/26
        if nome in df26_map:
            d26 = df26_map[nome]
            gf = int(d26['Gf'])
            ass = int(d26['Ass'])
            pv = int(d26['Pv'])
            fm26 = float(d26['Fm'])
        else:
            gf, ass, pv, fm26 = 0, 0, 0, 0.0

        gol_scorso_anno.append(gf)
        ass_scorso_anno.append(ass)
        part_scorso_anno.append(pv)

        # CONTINUITÀ (0-100 basata solo sul campionato scorso)
        if pv >= 30:
            cont = 100
        elif pv > 0:
            cont = max(35, int((pv / 38) * 100))
        else:
            cont = 60 if fvm >= 25 else (40 if fvm >= 10 else 20)
        cont_list.append(cont)

        # PERFORMANCE ATTESA (Algoritmo Predittivo Nascosto)
        # Combina Fm storica (se esistente) + FVM + Impatto parziale 2026/27 + bonus fermo
        fm_base = fm26 if pv >= 10 else (5.2 + (fvm / 12.0))
        fm_live = row['Fm'] if row['Pv'] > 0 else fm_base
        
        score = (fm_base * 0.75) + (fm_live * 0.25)
        if row['Rigorista'] == 1:
            score += 0.45
        elif row['Rigorista'] == 2:
            score += 0.15
        if row['Piazzati'] == 1:
            score += 0.20

        perf_normalizzata = int(min(99, max(50, 46 + (score - 5.0) * 13 + (fvm / 16.0))))
        perf_list.append(perf_normalizzata)

    df27['Gol_25_26'] = gol_scorso_anno
    df27['Ass_25_26'] = ass_scorso_anno
    df27['Part_25_26'] = part_scorso_anno
    df27['Continuita'] = cont_list
    df27['Performance'] = perf_list

    return df27

df_master = carica_master_dataset()

# --- 2. STATO ASTA ---
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
    st.subheader("Registra Acquisto Live")
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
        if st.button("🔄 Reset"):
            st.session_state.spesa_totale = 0
            st.session_state.giocatori_chiamati = []
            st.rerun()

# --- 4. PREZZI CONSIGLIATI (Scala 500 crediti) ---
df_calcolato = df_master.copy()
df_calcolato['Chiamato'] = df_calcolato['Nome'].isin(st.session_state.giocatori_chiamati)

fattore_scala = budget_iniziale / 1000.0
prezzi = []

for _, r in df_calcolato.iterrows():
    fvm = r['FVM_Ufficiale']
    ruolo = r['R']
    
    pr = fvm * fattore_scala
    if r['Rigorista'] == 1:
        pr *= 1.10
    if mod_difesa and ruolo == 'D':
        pr *= 1.15

    prezzi.append(max(1, int(round(pr))))

df_calcolato['Pr_Consig'] = prezzi

# --- 5. INTERFACCIA UTENTE ---
tab_listone, tab_asta = st.tabs(["📋 Listone", "🔨 Asta Live"])

with tab_listone:
    c_search, c_filter, c_order = st.columns([3, 2, 2])
    with c_search:
        cerca = st.text_input("🔍 Cerca giocatore o squadra", placeholder="Es. Martinez L., Dimarco, Inter...")
    with c_filter:
        filtro_r = st.selectbox("Filtra Ruolo", ["Tutti", "P", "D", "C", "A"])
    with c_order:
        ordina_per = st.selectbox("Ordina per", ["Performance", "Pr. Consig.", "Gol", "Assist", "Partite"])

    col_map = {
        "Performance": "Performance", 
        "Pr. Consig.": "Pr_Consig", 
        "Gol": "Gol_25_26", 
        "Assist": "Ass_25_26", 
        "Partite": "Part_25_26"
    }
    
    view_df = df_calcolato[~df_calcolato['Chiamato']].copy()
    if cerca:
        view_df = view_df[view_df['Nome'].str.contains(cerca, case=False, na=False) | view_df['Squadra'].str.contains(cerca, case=False, na=False)]
    if filtro_r != "Tutti":
        view_df = view_df[view_df['R'] == filtro_r]

    view_df = view_df.sort_values(by=col_map[ordina_per], ascending=False)

    colonne_finali = ['Nome', 'Squadra', 'R', 'Pr_Consig', 'Performance', 'Continuita', 'Gol_25_26', 'Ass_25_26', 'Part_25_26']
    st.dataframe(
        view_df[colonne_finali].rename(columns={
            'Pr_Consig': 'Pr. Consig. (cr)',
            'Performance': 'Performance /100',
            'Continuita': 'Continuità /100',
            'Gol_25_26': 'Gol',
            'Ass_25_26': 'Assist',
            'Part_25_26': 'Partite'
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
    colC.metric("Giocatori Acquistati", f"{len(st.session_state.giocatori_chiamati)}")
    
    st.markdown("---")
    st.subheader("Cronologia Chiamate")
    if st.session_state.giocatori_chiamati:
        st.write(" • ".join(reversed(st.session_state.giocatori_chiamati[-15:])))
    else:
        st.info("Nessun acquisto ancora registrato.")
