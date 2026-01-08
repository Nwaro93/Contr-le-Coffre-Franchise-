import streamlit as st
import pandas as pd
from datetime import date
from fpdf import FPDF
import os
import base64
import firebase_config
import auth_page

# --- Configuration de la page ---
st.set_page_config(page_title="Controle et Audit du Coffre", layout="wide", page_icon="🍗")

# Initialiser Firebase
db = firebase_config.init_firebase()

# Initialiser les variables de session
auth_page.init_session_state()

# Page de connexion
if not st.session_state.authenticated:
    auth_page.show_login_page()
    st.stop()

# Bouton de déconnexion
auth_page.show_logout_button()

# --- Fonction pour charger le logo en base64 ---
def get_logo_base64():
    logo_path = "kFC_logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()

# --- CSS Custom ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .main { background-color: #f5f5f5; }
    
    /* Header avec logo */
    .main-header {
        background: white;
        padding: 15px 25px;
        border-radius: 8px;
        margin-bottom: 20px;
        border-left: 4px solid #4a4a4a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .main-header img { height: 50px; }
    .main-header h1 { color: #333; font-size: 1.5em; font-weight: 600; margin: 0; }
    
    /* Premium Card */
    .premium-card {
        background: linear-gradient(135deg, #4a4a4a 0%, #2d2d2d 100%);
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .premium-card img { height: 45px; border-radius: 5px; }
    .premium-card-content h3 { margin: 0; font-size: 0.85em; font-weight: 400; opacity: 0.9; }
    .premium-card-content h2 { margin: 0; font-size: 1.1em; font-weight: 700; }
    
    /* Section Box */
    .section-box {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .section-title {
        font-weight: 600;
        color: #333;
        font-size: 0.95em;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #4a4a4a;
    }
    
    /* Data Table */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9em;
    }
    .data-table td {
        padding: 6px 10px;
        border-bottom: 1px solid #eee;
    }
    .data-table td:last-child {
        text-align: right;
        font-weight: 500;
    }
    .data-table tr.total {
        font-weight: bold;
        border-top: 2px solid #4a4a4a;
        color: #2d2d2d;
    }
    
    /* Result Cards */
    .result-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .result-card.dark {
        background: #2d2d2d;
        color: white;
    }
    .result-label {
        font-size: 0.8em;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .result-card.dark .result-label { color: #aaa; }
    .result-value {
        font-size: 1.6em;
        font-weight: 700;
        color: #333;
    }
    .result-card.dark .result-value { color: #ffd700; }
    .ecart-positive { color: #00c853 !important; }
    .ecart-negative { color: #e4002b !important; }
    
    /* Input styling compact */
    .stNumberInput > div > div > input {
        text-align: right !important;
        font-weight: 600 !important;
        padding: 8px 10px !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background: white; }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #4a4a4a;
        font-size: 0.95em;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    
    /* Hide branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Compact inputs */
    .compact-input label { font-size: 0.85em !important; }
    
    /* Info display */
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        font-size: 0.9em;
        border-bottom: 1px solid #eee;
    }
    .info-row span:first-child { color: #666; }
    .info-row span:last-child { font-weight: 500; color: #333; }
</style>
""", unsafe_allow_html=True)

# --- VALEURS ---
VALEURS_ROULEAUX = {
    "2 EUR": 50.0, "1 EUR": 25.0, "0.50 EUR": 20.0, "0.20 EUR": 8.0,
    "0.10 EUR": 4.0, "0.05 EUR": 2.5, "0.02 EUR": 1.0, "0.01 EUR": 0.5
}
VALEURS_BILLETS = {"100 EUR": 100, "50 EUR": 50, "20 EUR": 20, "10 EUR": 10, "5 EUR": 5}
VALEURS_PIECES = {
    "2 EUR": 2.0, "1 EUR": 1.0, "0.50 EUR": 0.50, "0.20 EUR": 0.20,
    "0.10 EUR": 0.10, "0.05 EUR": 0.05, "0.02 EUR": 0.02, "0.01 EUR": 0.01
}

def calc_billets(q): return sum(q.get(d, 0) * VALEURS_BILLETS[d] for d in VALEURS_BILLETS)
def calc_rouleaux(q): return sum(q.get(d, 0) * VALEURS_ROULEAUX[d] for d in VALEURS_ROULEAUX)
def calc_pieces(q): return sum(q.get(d, 0) * VALEURS_PIECES[d] for d in VALEURS_PIECES)

# --- PDF ---
class KFCPDF(FPDF):
    def header(self):
        self.set_fill_color(74, 74, 74)
        self.rect(0, 0, self.w, 22, 'F')
        if os.path.exists("kFC_logo.png"):
            self.image("kFC_logo.png", 8, 3, 18)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(30, 6)
        self.cell(0, 10, "RAPPORT DE CONTROLE COFFRE", align='L')
        self.ln(20)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, f"Page {self.page_no()} | {date.today()}", align='C')

def generate_pdf(data):
    pdf = KFCPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Infos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(0)
    pdf.cell(0, 8, "INFORMATIONS GENERALES", border=1, fill=True, align='L')
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Date: {data['Date']}")
    pdf.cell(95, 6, f"Restaurant: {data['Restaurant']}")
    pdf.ln()
    pdf.cell(95, 6, f"Controleur: {data['Controleur']}")
    pdf.cell(95, 6, f"Statut: {data['Statut']}")
    pdf.ln()
    pdf.cell(95, 6, f"Temoin: {data['Temoin']}")
    pdf.cell(95, 6, f"Cible: {data['Cible']:.2f} EUR")
    pdf.ln(8)
    
    # Fond de Coffre
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "FOND DE COFFRE", border=1, fill=True, align='L')
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(63, 6, f"Billets: {data['Val_Billets']:.2f} EUR")
    pdf.cell(63, 6, f"Rouleaux: {data['Val_Rouleaux']:.2f} EUR")
    pdf.cell(63, 6, f"Pieces: {data['Val_Pieces_Coffre']:.2f} EUR")
    pdf.ln()
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 6, f"Total Fond: {data['Val_Fond']:.2f} EUR")
    pdf.ln(8)
    
    # Petite Caisse
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "PETITE CAISSE", border=1, fill=True, align='L')
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Especes: {data['PC_Especes']:.2f} EUR")
    pdf.cell(95, 6, f"Factures: {data['PC_Factures']:.2f} EUR")
    pdf.ln()
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 6, f"Total PC: {data['Val_PC']:.2f} EUR")
    pdf.ln(8)
    
    # Caissons
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "CAISSONS", border=1, fill=True, align='L')
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 6, f"Billets: {data['Caissons_Billets']:.2f} EUR")
    pdf.cell(95, 6, f"Pieces: {data['Caissons_Pieces']:.2f} EUR")
    pdf.ln()
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 6, f"Total Caissons: {data['Val_Caissons']:.2f} EUR")
    pdf.ln(10)
    
    # Resume
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(45, 45, 45)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "RESUME FINAL", border=1, fill=True, align='C')
    pdf.ln()
    pdf.set_text_color(0)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(95, 8, "TOTAL CONSTATE:")
    pdf.cell(95, 8, f"{data['Total']:.2f} EUR", align='R')
    pdf.ln()
    pdf.cell(95, 8, "CIBLE:")
    pdf.cell(95, 8, f"{data['Cible']:.2f} EUR", align='R')
    pdf.ln()
    pdf.cell(95, 8, "ECART:")
    if data['Ecart'] != 0:
        pdf.set_text_color(228, 0, 43)
    else:
        pdf.set_text_color(0, 128, 0)
    pdf.cell(95, 8, f"{data['Ecart']:+.2f} EUR", align='R')
    pdf.set_text_color(0)
    
    # Commentaire
    if data.get('Commentaire'):
        pdf.ln(10)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "COMMENTAIRES", border=1, fill=True, align='L')
        pdf.ln()
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, data['Commentaire'])
    
    # Signatures
    pdf.ln(15)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 5, "Signature Controleur", align='C')
    pdf.cell(95, 5, "Signature Temoin", align='C')
    pdf.ln(12)
    pdf.line(20, pdf.get_y(), 90, pdf.get_y())
    pdf.line(120, pdf.get_y(), 190, pdf.get_y())
    
    return bytes(pdf.output())

# --- SIDEBAR ---
with st.sidebar:
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="height:60px;margin-bottom:10px;">', unsafe_allow_html=True)
    
    st.markdown("### ⚙️ Parametres")
    
    st.markdown("### 🏪 Restaurant")
    restaurant = st.text_input("Restaurant", placeholder="KFC Paris Nord", label_visibility="collapsed")
    
    st.markdown("### 👤 Controleur")
    controleur = st.text_input("Controleur", placeholder="Nom Prenom", label_visibility="collapsed")
    statut = st.selectbox("Statut", ["Directeur", "Assistant Manager", "Superviseur", "Responsable de service"])
    
    st.markdown("### 👥 Temoin")
    temoin = st.text_input("Temoin", placeholder="Nom du temoin", label_visibility="collapsed")
    
    st.markdown("### 💬 Commentaire")
    commentaire = st.text_area("Commentaire", placeholder="Observations...", height=80, label_visibility="collapsed")
    
    st.markdown("### ✍️ Signature")
    st.caption("Signatures requises sur le PDF")

# --- MAIN HEADER ---
header_html = f'''
<div class="main-header">
    {"<img src='data:image/png;base64," + logo_b64 + "'/>" if logo_b64 else "🍗"}
    <h1>Controle et Audit du Coffre</h1>
</div>
'''
st.markdown(header_html, unsafe_allow_html=True)

# Layout 2 colonnes
col_left, col_right = st.columns([1, 1])

# === COLONNE GAUCHE ===
with col_left:
    # Audit Data
    st.markdown('<div class="section-box"><div class="section-title">📋 Audit Data</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        date_ctrl = st.date_input("Date", value=date.today())
    with c2:
        cible = st.number_input("Cible (EUR)", value=1800.00, step=100.0, format="%.2f")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fond de Coffre
    st.markdown('<div class="section-box"><div class="section-title">💵 Fond de Coffre</div>', unsafe_allow_html=True)
    
    # Billets avec valeurs
    st.markdown("**Billets**")
    cols_b = st.columns(5)
    q_billets = {}
    for i, (denom, val) in enumerate(VALEURS_BILLETS.items()):
        with cols_b[i]:
            q_billets[denom] = st.number_input(f"{denom}", min_value=0, value=0, key=f"b_{denom}", help=f"Valeur: {val} EUR/billet")
    total_billets = calc_billets(q_billets)
    
    # Rouleaux avec aide sur valeur
    st.markdown("**Rouleaux** *(valeur par rouleau)*")
    cols_r1 = st.columns(4)
    q_rouleaux = {}
    roul_list = list(VALEURS_ROULEAUX.items())
    for i, (denom, val) in enumerate(roul_list[:4]):
        with cols_r1[i]:
            q_rouleaux[denom] = st.number_input(f"{denom}", min_value=0, value=0, key=f"r_{denom}", help=f"={val} EUR/roul")
    cols_r2 = st.columns(4)
    for i, (denom, val) in enumerate(roul_list[4:]):
        with cols_r2[i]:
            q_rouleaux[denom] = st.number_input(f"{denom}", min_value=0, value=0, key=f"r_{denom}", help=f"={val} EUR/roul")
    total_rouleaux = calc_rouleaux(q_rouleaux)
    
    # Pièces en vrac dans le coffre
    st.markdown("**Pieces en vrac** *(nombre de pieces)*")
    cols_p1 = st.columns(4)
    q_pieces_coffre = {}
    pieces_list = list(VALEURS_PIECES.items())
    for i, (denom, val) in enumerate(pieces_list[:4]):
        with cols_p1[i]:
            q_pieces_coffre[denom] = st.number_input(f"{denom}", min_value=0, value=0, key=f"pc_{denom}", help=f"Valeur: {val} EUR")
    cols_p2 = st.columns(4)
    for i, (denom, val) in enumerate(pieces_list[4:]):
        with cols_p2[i]:
            q_pieces_coffre[denom] = st.number_input(f"{denom}", min_value=0, value=0, key=f"pc_{denom}", help=f"Valeur: {val} EUR")
    total_pieces_coffre = calc_pieces(q_pieces_coffre)
    
    val_fond = total_billets + total_rouleaux + total_pieces_coffre
    
    st.markdown(f"""
    <table class="data-table">
        <tr><td>Billets</td><td>{total_billets:.2f} EUR</td></tr>
        <tr><td>Rouleaux</td><td>{total_rouleaux:.2f} EUR</td></tr>
        <tr><td>Pieces en vrac</td><td>{total_pieces_coffre:.2f} EUR</td></tr>
        <tr class="total"><td>Total Fond</td><td>{val_fond:.2f} EUR</td></tr>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# === COLONNE DROITE ===
with col_right:
    # Premium Card avec logo
    premium_html = f'''
    <div class="premium-card">
        {"<img src='data:image/png;base64," + logo_b64 + "'/>" if logo_b64 else ""}
        <div class="premium-card-content">
            <h3>RAPPORT DE CONTROLE COFFRE</h3>
            <h2>{restaurant if restaurant else "KFC Restaurant"}</h2>
        </div>
    </div>
    '''
    st.markdown(premium_html, unsafe_allow_html=True)
    
    # Informations Generales
    st.markdown('<div class="section-box"><div class="section-title">📄 Informations Generales</div>', unsafe_allow_html=True)
    
    st.markdown(f'''
    <div class="info-row"><span>Date</span><span>{date_ctrl}</span></div>
    <div class="info-row"><span>Cible</span><span>{cible:.2f} EUR</span></div>
    <div class="info-row"><span>Responsable</span><span>{controleur if controleur else "-"}</span></div>
    <div class="info-row"><span>Statut</span><span>{statut}</span></div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section Petite Caisse
    st.markdown('<div class="section-box"><div class="section-title">💰 Petite Caisse</div>', unsafe_allow_html=True)
    
    st.markdown("**Especes et Factures**")
    col_pce, col_pcf = st.columns(2)
    with col_pce:
        pc_especes = st.number_input("💵 Especes (EUR)", min_value=0.0, value=0.0, step=5.0, format="%.2f", key="pc_esp")
    with col_pcf:
        pc_factures = st.number_input("🧾 Factures (EUR)", min_value=0.0, value=0.0, step=5.0, format="%.2f", key="pc_fact")
    val_pc = pc_especes + pc_factures
    
    st.markdown(f"""
    <table class="data-table">
        <tr><td>Especes</td><td>{pc_especes:.2f} EUR</td></tr>
        <tr><td>Factures</td><td>{pc_factures:.2f} EUR</td></tr>
        <tr class="total"><td>Total Petite Caisse</td><td>{val_pc:.2f} EUR</td></tr>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# === SECTION CAISSONS (pleine largeur) ===
st.markdown('<div class="section-box"><div class="section-title">🗃️ Caissons (Tiroirs-caisses)</div>', unsafe_allow_html=True)

# Billets dans les caissons
st.markdown("**Billets dans les caissons** *(nombre de billets)*")
cols_cb = st.columns(5)
q_caissons_billets = {}
for i, (denom, val) in enumerate(VALEURS_BILLETS.items()):
    with cols_cb[i]:
        q_caissons_billets[denom] = st.number_input(f"{denom}", min_value=0, value=0, key=f"cb_{denom}", help=f"Valeur: {val} EUR")
caissons_billets = calc_billets(q_caissons_billets)

# Pièces dans les caissons
st.markdown("**Pieces dans les caissons** *(nombre de pieces)*")
pieces_list_cais = list(VALEURS_PIECES.items())
cols_cp1 = st.columns(4)
q_caissons_pieces = {}
for i, (denom, val) in enumerate(pieces_list_cais[:4]):
    with cols_cp1[i]:
        q_caissons_pieces[denom] = st.number_input(f"{denom}", min_value=0, value=0, key=f"cp_{denom}", help=f"Valeur: {val} EUR")
cols_cp2 = st.columns(4)
for i, (denom, val) in enumerate(pieces_list_cais[4:]):
    with cols_cp2[i]:
        q_caissons_pieces[denom] = st.number_input(f"{denom}", min_value=0, value=0, key=f"cp_{denom}", help=f"Valeur: {val} EUR")
caissons_pieces = calc_pieces(q_caissons_pieces)

val_caissons = caissons_billets + caissons_pieces

st.markdown(f"""
<table class="data-table">
    <tr><td>Billets caissons</td><td>{caissons_billets:.2f} EUR</td></tr>
    <tr><td>Pieces caissons</td><td>{caissons_pieces:.2f} EUR</td></tr>
    <tr class="total"><td>Total Caissons</td><td>{val_caissons:.2f} EUR</td></tr>
</table>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

total_general = val_fond + val_pc + val_caissons
    
# --- SYNTHESE GLOBALE ---
st.markdown('<div class="section-box"><div class="section-title">📊 Synthese Globale</div>', unsafe_allow_html=True)

st.markdown(f"""
<table class="data-table">
    <tr><td>Fond de Coffre (Billets + Rouleaux + Pieces)</td><td>{val_fond:.2f} EUR</td></tr>
    <tr><td>Petite Caisse (Especes + Factures)</td><td>{val_pc:.2f} EUR</td></tr>
    <tr><td>Caissons (Billets + Pieces)</td><td>{val_caissons:.2f} EUR</td></tr>
    <tr class="total"><td>TOTAL GENERAL</td><td>{total_general:.2f} EUR</td></tr>
</table>
""", unsafe_allow_html=True)

if commentaire:
    st.markdown(f"**Commentaire:** {commentaire}")

st.markdown('</div>', unsafe_allow_html=True)

# --- RESUME FINAL ---
st.markdown("---")

total_constate = val_fond + val_pc + val_caissons
ecart = total_constate - cible

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    st.markdown(f'''
    <div class="result-card">
        <div class="result-label">TOTAL CONSTATE</div>
        <div class="result-value">{total_constate:.2f} EUR</div>
    </div>
    ''', unsafe_allow_html=True)

with col_r2:
    st.markdown(f'''
    <div class="result-card dark">
        <div class="result-label">CIBLE</div>
        <div class="result-value">{cible:.2f} EUR</div>
    </div>
    ''', unsafe_allow_html=True)

with col_r3:
    ecart_class = "ecart-positive" if ecart >= 0 else "ecart-negative"
    ecart_icon = "🟢" if ecart >= 0 else "🔴"
    st.markdown(f'''
    <div class="result-card">
        <div class="result-label">ECART {ecart_icon}</div>
        <div class="result-value {ecart_class}">{ecart:+.2f} EUR</div>
    </div>
    ''', unsafe_allow_html=True)

# --- BOUTONS ---
st.markdown("<br>", unsafe_allow_html=True)

col_b1, col_b2, col_b3 = st.columns([1, 1, 1])

with col_b1:
    validate_btn = st.button("✅ Valider, Sauvegarder", type="primary", use_container_width=True)

with col_b2:
    pdf_btn = st.button("📄 Generer PDF", type="secondary", use_container_width=True)

with col_b3:
    reset_btn = st.button("🔄 Reset Formulaire", type="secondary", use_container_width=True)

# Gestion du Reset
if reset_btn:
    st.session_state.clear()
    st.rerun()

# Checkbox combiné
auto_action = st.checkbox("☑️ Valider, Sauvegarder et Generer PDF automatiquement")

if validate_btn or pdf_btn or auto_action:
    if not temoin or not restaurant or not controleur:
        st.error("⚠️ Veuillez remplir: Restaurant, Controleur et Temoin dans la barre laterale")
    else:
        audit_data = {
            "Restaurant": restaurant,
            "Date": str(date_ctrl),
            "Controleur": controleur,
            "Statut": statut,
            "Temoin": temoin,
            "Cible": cible,
            "Q_Billets": q_billets,
            "Q_Rouleaux": q_rouleaux,
            "Val_Billets": total_billets,
            "Val_Rouleaux": total_rouleaux,
            "Val_Pieces_Coffre": total_pieces_coffre,
            "Val_Fond": val_fond,
            "PC_Especes": pc_especes,
            "PC_Factures": pc_factures,
            "Val_PC": val_pc,
            "Caissons_Billets": caissons_billets,
            "Caissons_Pieces": caissons_pieces,
            "Val_Caissons": val_caissons,
            "Total": total_constate,
            "Ecart": ecart,
            "Commentaire": commentaire
        }
        
        if validate_btn or auto_action:
            csv_data = {
                "Restaurant": restaurant, "Date": str(date_ctrl), "Controleur": controleur,
                "Statut": statut, "Temoin": temoin, "Cible": cible,
                "Val_Fond": val_fond, "Val_PC": val_pc, "Val_Caissons": val_caissons,
                "Total": total_constate, "Ecart": ecart
            }
            pd.DataFrame([csv_data]).to_csv("historique_kfc.csv", mode='a', index=False, 
                                            header=not os.path.exists("historique_kfc.csv"))
            st.success("✅ Controle valide et sauvegarde!")
        
        if pdf_btn or validate_btn or auto_action:
            pdf_out = generate_pdf(audit_data)
            st.download_button(
                label="📥 Telecharger le Rapport PDF",
                data=pdf_out,
                file_name=f"Controle_KFC_{restaurant}_{date_ctrl}.pdf",
                mime="application/pdf"
            )

# --- HISTORIQUE ---
with st.expander("📜 Historique des Controles"):
    if os.path.exists("historique_kfc.csv"):
        df = pd.read_csv("historique_kfc.csv")
        
        if len(df) > 0:
            # Ajouter un index pour identification
            df_display = df.copy()
            df_display.insert(0, 'ID', range(1, len(df) + 1))
            
            st.dataframe(df_display, use_container_width=True)
            
            # Section suppression (Admin uniquement)
            if auth_page.is_admin():
                st.markdown("---")
                st.markdown("**🗑️ Supprimer un audit** (Admin uniquement)")
                
                col_del1, col_del2 = st.columns([2, 1])
                
                with col_del1:
                    # Sélecteur pour choisir l'audit à supprimer
                    options = [f"ID {i+1} - {df.iloc[i]['Restaurant']} ({df.iloc[i]['Date']})" for i in range(len(df))]
                    selected = st.selectbox("Selectionner l'audit a supprimer", options, key="delete_select")
                
                with col_del2:
                    if st.button("❌ Supprimer", type="secondary", use_container_width=True):
                        # Extraire l'index de l'audit sélectionné
                        idx = int(selected.split(" ")[1]) - 1
                        df = df.drop(df.index[idx]).reset_index(drop=True)
                        
                        if len(df) > 0:
                            df.to_csv("historique_kfc.csv", index=False)
                        else:
                            os.remove("historique_kfc.csv")
                        
                        st.success(f"✅ Audit supprime!")
                        st.rerun()
                
                # Bouton pour tout supprimer
                st.markdown("---")
                if st.button("🗑️ Supprimer tout l'historique", type="secondary"):
                    os.remove("historique_kfc.csv")
                    st.success("✅ Historique completement supprime!")
                    st.rerun()
            else:
                st.info("🔒 Seul l'administrateur peut supprimer les archives.")
        else:
            st.info("Aucun historique disponible.")
    else:
        st.info("Aucun historique disponible.")

# --- PANNEAU ADMIN ---
auth_page.show_admin_panel()
