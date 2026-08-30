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
    f_stat25 = trova_file("Statistiche_Fantacalcio_Stagione_2024_25_Statistico.xlsx")
    f_quot27 = trova_file("Quotazioni_Fantacalcio_Stagione_2026_27.xlsx")
    
    def pulisci_df(path):
        if not path or not os.path.exists(path):
            return pd.DataFrame()
        d = pd.read_excel(path, header=1)
        d.columns = d.columns.str.strip()
        for c in ['Pv', 'Mv', 'Fm', 'Gf', 'Ass', 'Gs', 'Rp', 'Rc', 'Qt. A', 'Qt. I', 'FVM']:
            if c in d.columns:
                if d[c].dtype == object:
                    d[c] = d[c].astype(str).str.replace(',', '.')
                d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0.0)
        return d

    df27 = pulisci_df(f_stat27)
    df26 = pulisci_df(f_stat26)
    df25 = pulisci_df(f_stat25)
    df_q = pulisci_df(f_quot27)

    if df27.empty:
        st.error("❌ File statistiche 2026/27 non trovato.")
        st.stop()

    # Mappe storiche
    df26_map = df26.set_index('Nome')[['Fm', 'Pv', 'Gf', 'Ass']].to_dict('index') if not df26.empty else {}
    df25_map = df25.set_index('Nome')[['Fm', 'Pv']].to_dict('index') if not df25.empty else {}
    
    # Mappa quotazioni ufficiali
    fvm_map = {}
    if not df_q.empty and 'Nome' in df_q.columns:
        col_fvm = 'FVM' if 'FVM' in df_q.columns else ('Qt. A' if 'Qt. A' in df_q.columns else 'Qt. I')
        fvm_map = df_q.set_index('Nome')[col_fvm].to_dict()

    df27['Rigorista'] = df27['Nome'].map(RIGORISTI).fillna(0).astype(int)
    df27['Piazzati'] = df27['Nome'].map(PIAZZATI).fillna(0).astype(int)
    df27['Quotazione_Ufficiale'] = df27['Nome'].map(fvm_map).fillna(1.0)

    # Stabilizzazione FantaMedia: se stagione 26/27 ha < 5 partite, pesa lo storico 25/26
    fm_proiettata, continuita_list, gol_list, ass_list, part_list = [], [], [], [], []

    for _, row in df27.iterrows():
        nome = row['Nome']
        fm27, pv27 = row['Fm'], row['Pv']
        d26 = df26_map.get(nome, {'Fm': 0.0, 'Pv': 0, 'Gf': 0, 'Ass': 0})
        d25 = df25_map.get(nome, {'Fm': 0.0, 'Pv': 0})

        tot_gol = row['Gf'] + d26['Gf']
        tot_ass = row['Ass'] + d26['Ass']
        tot_pv = pv27 + d26['Pv']
        gol_list.append(int(tot_gol))
        ass_list.append(int(tot_ass))
        part_list.append(int(tot_pv))

        # Calcolo Fm attesa normalizzata (evita FantaMedie da 13.0 su 1 partita)
        if d26['Pv'] >= 10:
            fm_calc = (d26['Fm'] * 0.85) + (fm27 * 0.15 if pv27 > 0 else 0)
            cont = min(100, int((d26['Pv'] / 38) * 100))
        elif d25['Pv'] >= 10:
            fm_calc = (d25['Fm'] * 0.85)
            cont = min(100, int((d25['Pv'] / 38) * 85))
        elif pv27 > 0:
            # Nuovo acquisto / esordiente con 1-2 partite: ancora la Fm al FVM
            q_val = df27.loc[df27['Nome'] == nome, 'Quotazione_Ufficiale'].values[0]
            fm_calc = min(7.5, max(5.5, 5.0 + (q_val / 10.0)))
            cont = 65
        else:
            fm_calc = 5.5
            cont = 45

        fm_proiettata.append(fm_calc)
        continuita_list.append(cont)

    df27['Fm_Proiettata'] = fm_proiettata
    df27['Continuita'] = continuita_list
    df27['Tot_Gol'] = gol_list
    df27['Tot_Ass'] = ass_list
    df27['Tot_Part'] = part_list

    # GOAT Score
    bonus_rig = np.where(df27['Rigorista'] == 1, 0.40, np.where(df27['Rigorista'] == 2, 0.15, 0.0))
    bonus_piaz = np.where(df27['Piazzati'] == 1, 0.20, 0.0)
    df27['GOAT_Score'] = df27['Fm_Proiettata'] + bonus_rig + bonus_piaz

    # Performance normalizzata da 50 a 99
    for r in ['P', 'D', 'C', 'A']:
        m = df27['R'] == r
        min_v, max_v = df27.loc[m, 'GOAT_Score'].min(), df27.loc[m, 'GOAT_Score'].max()
        if max_v > min_v:
            df27.loc[m, 'Performance'] = ((df27.loc[m, 'GOAT_Score'] - min_v) / (max_v - min_v) * 44 + 55).astype(int)
        else:
            df27.loc[m, 'Performance'] = 60

    return df27

df_master = carica_master_dataset()

# --- 2. STATO ASTA ---
if 'spesa_totale' not in st.session_state:
    st.session_state.spesa_totale = 0
if 'giocatori_chiamati' not in st.session_state:
    st.session_state.giocatori_chiamati = []

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Pannello Asta")
    partecipanti = st.radio("Partecipanti Lega", [10, 12], index=0)
    budget_iniziale = st.number_input("Budget Singolo Team", value=500, step=50)
    mod_difesa = st.checkbox("Modificatore Difesa", value=False)
    
    st.markdown("---")
    st.subheader("Registra Acquisto")
    giocatori_disponibili = [g for g in df_master['Nome'].unique() if g not in st.session_state.giocatori_chiamati]
    giocatore_selezionato = st.selectbox("Giocatore battuto", ["-"] + sorted(giocatori_disponibili))
    prezzo_effettivo = st.number_input("Prezzo pagato", min_value=1, value=1, step=1)
    
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

# --- 4. ALGORITMO VALUTAZIONE (CALIBRATO SUL BUDGET SINGOLO) ---
budget_per_squadra = budget_iniziale
# Ripartizione target del budget da 500cr per una squadra tipo
target_budget_ruolo = {'P': 0.08 * budget_per_squadra, 'D': 0.12 * budget_per_squadra, 'C': 0.25 * budget_per_squadra, 'A': 0.55 * budget_per_squadra}
if mod_difesa:
    target_budget_ruolo = {'P': 0.08 * budget_per_squadra, 'D': 0.20 * budget_per_squadra, 'C': 0.22 * budget_per_squadra, 'A': 0.50 * budget_per_squadra}

slot_titolari = {'P': partecipanti * 1, 'D': partecipanti * 4, 'C': partecipanti * 4, 'A': partecipanti * 3}

df_calcolato = df_master.copy()
df_calcolato['Chiamato'] = df_calcolato['Nome'].isin(st.session_state.giocatori_chiamati)
df_disponibili = df_calcolato[~df_calcolato['Chiamato']].copy()

prezzi_consigliati = {}
for ruolo in ['P', 'D', 'C', 'A']:
    sub = df_disponibili[df_disponibili['R'] == ruolo].sort_values(by='GOAT_Score', ascending=False)
    n_tit = slot_titolari[ruolo]
    
    valore_rimpiazzo = sub.iloc[n_tit - 1]['GOAT_Score'] if len(sub) > n_tit else sub['GOAT_Score'].min()
    sub['VOR'] = (sub['GOAT_Score'] - valore_rimpiazzo).clip(lower=0)
    somma_vor = sub['VOR'].sum()
    budget_reparto_singolo = target_budget_ruolo[ruolo]

    for _, r in sub.iterrows():
        if somma_vor > 0 and r['VOR'] > 0:
            # Calcolo proporzionale sul budget di reparto della singola squadra
            pr = 1 + (r['VOR'] / somma_vor) * (budget_reparto_singolo * (n_tit / partecipanti) - (n_tit / partecipanti))
            # Calibrazione sui top: un top A non può superare il 32-35% del budget (160-175 cr)
            max_cap = 175 if ruolo == 'A' else (75 if ruolo == 'C' else 45)
            prezzi_consigliati[r['Nome']] = min(max_cap, max(1, int(round(pr))))
        else:
            prezzi_consigliati[r['Nome']] = 1

df_calcolato['Pr_Consig'] = df_calcolato['Nome'].map(prezzi_consigliati).fillna(1).astype(int)

# --- 5. INTERFACCIA UTENTE (LISTONE / ASTA) ---
tab_listone, tab_asta = st.tabs(["📋 Listone", "🔨 Asta Live"])

with tab_listone:
    c_search, c_filter, c_order = st.columns([3, 2, 2])
    with c_search:
        cerca = st.text_input("🔍 Cerca giocatore o squadra", placeholder="Es. Martinez L., Roma, Inter...")
    with c_filter:
        filtro_r = st.selectbox("Filtra Ruolo", ["Tutti", "P", "D", "C", "A"])
    with c_order:
        ordina_per = st.selectbox("Ordina per", ["Pr. Consig.", "Performance", "Gol", "Assist", "Partite"])

    col_map = {"Pr. Consig.": "Pr_Consig", "Performance": "Performance", "Gol": "Tot_Gol", "Assist": "Tot_Ass", "Partite": "Tot_Part"}
    
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
    colA.metric("Crediti Residui Lega", f"{residuo_lega} cr")
    colB.metric("Crediti Spesi Totali", f"{st.session_state.spesa_totale} cr")
    colC.metric("Giocatori Acquistati", f"{len(st.session_state.giocatori_chiamati)}")
    
    st.markdown("---")
    st.subheader("Ultime Chiamate Registrate")
    if st.session_state.giocatori_chiamati:
        st.write(" • ".join(reversed(st.session_state.giocatori_chiamati[-15:])))
    else:
        st.info("Nessun giocatore acquistato finora. Inserisci i dati dalla barra laterale.")
