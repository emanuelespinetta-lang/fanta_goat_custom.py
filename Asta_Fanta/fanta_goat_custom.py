import pandas as pd
import streamlit as st
import numpy as np
import os

st.set_page_config(page_title="FantaGOAT Custom", layout="wide", initial_sidebar_state="expanded")

# --- 1. DIZIONARI TIRATORI ---
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
    f_curr = trova_file("Statistiche_Fantacalcio_Stagione_2026_27_Statistico.xlsx")
    f_prev1 = trova_file("Statistiche_Fantacalcio_Stagione_2025_26_Statistico.xlsx")
    f_prev2 = trova_file("Statistiche_Fantacalcio_Stagione_2024_25_Statistico.xlsx")
    
    def pulisci_df(path):
        if not path or not os.path.exists(path):
            return pd.DataFrame()
        d = pd.read_excel(path, header=1)
        d.columns = d.columns.str.strip()
        for c in ['Pv', 'Mv', 'Fm', 'Gf', 'Ass', 'Gs', 'Rp', 'Rc']:
            if c in d.columns:
                if d[c].dtype == object:
                    d[c] = d[c].astype(str).str.replace(',', '.')
                d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0.0)
        return d

    df27 = pulisci_df(f_curr)
    df26 = pulisci_df(f_prev1)
    df25 = pulisci_df(f_prev2)

    if df27.empty:
        st.error("File 2026/27 non trovato.")
        st.stop()

    df26_map = df26.set_index('Nome')[['Fm', 'Pv', 'Gf', 'Ass']].to_dict('index') if not df26.empty else {}
    df25_map = df25.set_index('Nome')[['Fm', 'Pv']].to_dict('index') if not df25.empty else {}

    df27['Rigorista'] = df27['Nome'].map(RIGORISTI).fillna(0).astype(int)
    df27['Piazzati'] = df27['Nome'].map(PIAZZATI).fillna(0).astype(int)

    # Calcolo Fm ponderata e storici
    fm_proiettata, continuita_list, gol_list, ass_list, part_list = [], [], [], [], []

    for _, row in df27.iterrows():
        nome = row['Nome']
        fm27, pv27 = row['Fm'], row['Pv']
        d26 = df26_map.get(nome, {'Fm': 0.0, 'Pv': 0, 'Gf': 0, 'Ass': 0})
        d25 = df25_map.get(nome, {'Fm': 0.0, 'Pv': 0})

        # Totali storici per visualizzazione
        tot_gol = row['Gf'] + d26['Gf']
        tot_ass = row['Ass'] + d26['Ass']
        tot_pv = pv27 + d26['Pv']
        gol_list.append(int(tot_gol))
        ass_list.append(int(tot_ass))
        part_list.append(int(tot_pv))

        # Media Ponderata Storica
        if d26['Pv'] > 10 and d25['Pv'] > 10:
            fm_calc = (fm27 * 0.15) + (d26['Fm'] * 0.55) + (d25['Fm'] * 0.30)
            cont = 100 if d26['Pv'] >= 28 else int((d26['Pv'] / 38) * 100)
        elif d26['Pv'] > 10:
            fm_calc = (fm27 * 0.20) + (d26['Fm'] * 0.80)
            cont = int((d26['Pv'] / 38) * 100)
        elif pv27 > 0:
            fm_calc = fm27
            cont = 60
        else:
            fm_calc = 5.5
            cont = 40

        fm_proiettata.append(fm_calc)
        continuita_list.append(cont)

    df27['Fm_Proiettata'] = fm_proiettata
    df27['Continuita'] = continuita_list
    df27['Tot_Gol'] = gol_list
    df27['Tot_Ass'] = ass_list
    df27['Tot_Part'] = part_list

    # GOAT Score (Performance)
    bonus_rig = np.where(df27['Rigorista'] == 1, 0.45, np.where(df27['Rigorista'] == 2, 0.20, 0.0))
    bonus_piaz = np.where(df27['Piazzati'] == 1, 0.25, 0.0)
    df27['GOAT_Score'] = df27['Fm_Proiettata'] + bonus_rig + bonus_piaz

    # Normalizzazione Performance 0-100 per ruolo
    for r in ['P', 'D', 'C', 'A']:
        m = df27['R'] == r
        min_v = df27.loc[m, 'GOAT_Score'].min()
        max_v = df27.loc[m, 'GOAT_Score'].max()
        if max_v > min_v:
            df27.loc[m, 'Performance'] = ((df27.loc[m, 'GOAT_Score'] - min_v) / (max_v - min_v) * 45 + 55).astype(int)
        else:
            df27.loc[m, 'Performance'] = 60

    return df27

df_master = carica_master_dataset()

# --- 2. GESTIONE STATO ASTA ---
if 'spesa_totale' not in st.session_state:
    st.session_state.spesa_totale = 0
if 'giocatori_chiamati' not in st.session_state:
    st.session_state.giocatori_chiamati = []

# --- 3. SIDEBAR CONFIGURAZIONE ---
with st.sidebar:
    st.title("⚙️ Setup Asta")
    partecipanti = st.radio("Partecipanti Lega", [10, 12], index=0)
    budget_iniziale = st.number_input("Budget Iniziale Squadra", value=500, step=50)
    mod_difesa = st.checkbox("Modificatore Difesa", value=False)
    
    st.markdown("---")
    st.subheader("Registra Giocatore Chiamato")
    giocatori_disponibili = [g for g in df_master['Nome'].unique() if g not in st.session_state.giocatori_chiamati]
    giocatore_selezionato = st.selectbox("Giocatore battuto", ["-"] + sorted(giocatori_disponibili))
    prezzo_effettivo = st.number_input("Prezzo finale pagato", min_value=1, value=1, step=1)
    
    if st.button("Conferma Acquisto"):
        if giocatore_selezionato != "-":
            st.session_state.giocatori_chiamati.append(giocatore_selezionato)
            st.session_state.spesa_totale += prezzo_effettivo
            st.rerun()

    if st.button("Reset Asta"):
        st.session_state.spesa_totale = 0
        st.session_state.giocatori_chiamati = []
        st.rerun()

# --- 4. MOTORE VOR (VALUE OVER REPLACEMENT) ---
budget_totale_lega = partecipanti * budget_iniziale
budget_residuo = max(1, budget_totale_lega - st.session_state.spesa_totale)

quota_reparto = {'P': 0.08, 'D': 0.10, 'C': 0.22, 'A': 0.60}
if mod_difesa:
    quota_reparto = {'P': 0.08, 'D': 0.18, 'C': 0.19, 'A': 0.55}

slot_titolari = {'P': partecipanti * 1, 'D': partecipanti * 5, 'C': partecipanti * 5, 'A': partecipanti * 3}

df_calcolato = df_master.copy()
df_calcolato['Chiamato'] = df_calcolato['Nome'].isin(st.session_state.giocatori_chiamati)
df_disponibili = df_calcolato[~df_calcolato['Chiamato']].copy()

prezzi_consigliati = {}
for ruolo in ['P', 'D', 'C', 'A']:
    sub = df_disponibili[df_disponibili['R'] == ruolo].sort_values(by='GOAT_Score', ascending=False)
    n_titolari = slot_titolari[ruolo]
    
    if len(sub) > n_titolari:
        valore_rimpiazzo = sub.iloc[n_titolari - 1]['GOAT_Score']
    else:
        valore_rimpiazzo = sub['GOAT_Score'].min() if not sub.empty else 0

    sub['VOR'] = (sub['GOAT_Score'] - valore_rimpiazzo).clip(lower=0)
    somma_vor = sub['VOR'].sum()
    budget_ruolo = budget_residuo * quota_reparto[ruolo]

    for _, r in sub.iterrows():
        if somma_vor > 0 and r['VOR'] > 0:
            pr = 1 + (r['VOR'] / somma_vor) * (budget_ruolo - len(sub))
            prezzi_consigliati[r['Nome']] = max(1, int(round(pr)))
        else:
            prezzi_consigliati[r['Nome']] = 1

df_calcolato['Pr_Consig'] = df_calcolato['Nome'].map(prezzi_consigliati).fillna(1).astype(int)

# --- 5. INTERFACCIA A SCHEDE (LISTONE / ASTA) ---
tab_listone, tab_asta = st.tabs(["📋 Listone", "🔨 Asta Live"])

with tab_listone:
    c_search, c_filter, c_order = st.columns([3, 2, 2])
    with c_search:
        cerca = st.text_input("🔍 Cerca giocatore", placeholder="Es. Martinez L., Dimarco...")
    with c_filter:
        filtro_r = st.selectbox("Ruolo", ["Tutti", "P", "D", "C", "A"])
    with c_order:
        ordina_per = st.selectbox("Ordina per", ["Performance", "Pr. Consig.", "Gol", "Assist", "Partite"])

    col_map = {"Performance": "Performance", "Pr. Consig.": "Pr_Consig", "Gol": "Tot_Gol", "Assist": "Tot_Ass", "Partite": "Tot_Part"}
    
    view_df = df_calcolato[~df_calcolato['Chiamato']]
    if cerca:
        view_df = view_df[view_df['Nome'].str.contains(cerca, case=False, na=False)]
    if filtro_r != "Tutti":
        view_df = view_df[view_df['R'] == filtro_r]

    view_df = view_df.sort_values(by=col_map[ordina_per], ascending=False)

    colonne_finali = ['Nome', 'Squadra', 'R', 'Pr_Consig', 'Performance', 'Continuita', 'Tot_Gol', 'Tot_Ass', 'Tot_Part']
    st.dataframe(
        view_df[colonne_finali].rename(columns={
            'Pr_Consig': 'Pr. Consig.',
            'Performance': 'Performance /100',
            'Continuita': 'Continuità /100',
            'Tot_Gol': 'Gol Storici',
            'Tot_Ass': 'Assist Storici',
            'Tot_Part': 'Partite'
        }),
        use_container_width=True,
        hide_index=True
    )

with tab_asta:
    st.metric("Crediti Totali Rimasti nella Lega", f"{budget_residuo} cr")
    st.write(f"**Giocatori già assegnati:** {len(st.session_state.giocatori_chiamati)}")
    if st.session_state.giocatori_chiamati:
        st.write(", ".join(st.session_state.giocatori_chiamati[-10:]))
