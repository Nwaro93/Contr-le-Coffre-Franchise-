import streamlit as st
import hashlib
import firebase_config
import os
import base64

def get_logo_base64():
    """Charge le logo KFC en base64"""
    logo_path = "kFC_logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def hash_password(password):
    """Hash le mot de passe avec SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_session_state():
    """Initialise les variables de session pour l'authentification"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

def show_login_page():
    """Affiche la page de connexion"""
    
    # CSS pour la page de connexion - Masquer TOUS les éléments Streamlit
    st.markdown("""
    <style>
        /* === MASQUER COMPLETEMENT LE BOUTON MANAGE APP === */
        
        /* Header complet */
        header, 
        header[data-testid="stHeader"],
        [data-testid="stHeader"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            position: absolute !important;
            top: -9999px !important;
        }
        
        /* Toolbar et boutons */
        [data-testid="stToolbar"],
        [data-testid="manage-app-button"],
        [data-testid="stStatusWidget"],
        [data-testid="stDecoration"],
        [data-testid="baseButton-header"],
        .stDeployButton,
        .stAppDeployButton {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Menu principal */
        #MainMenu,
        footer,
        button[kind="header"] {
            display: none !important;
        }
        
        /* Classes Streamlit Cloud specifiques */
        .viewerBadge_container__r5tak,
        .styles_viewerBadge__CvC9N,
        .viewerBadge_link__qRIco,
        ._profileContainer_gzau3_53,
        ._profilePreview_gzau3_63,
        .stAppViewBlockContainer [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* Classes emotion-cache dynamiques */
        .st-emotion-cache-zq5wmm,
        .st-emotion-cache-1wbqy5l,
        .st-emotion-cache-h4xjwg,
        .st-emotion-cache-1avcm0n,
        .st-emotion-cache-eczf16,
        .st-emotion-cache-10trblm,
        .st-emotion-cache-6qob1r {
            display: none !important;
        }
        
        /* Bouton hamburger et icones header */
        button[kind="headerNoPadding"],
        [data-testid="collapsedControl"],
        .css-1rs6os,
        .css-10trblm,
        .css-1dp5vir,
        .css-14xtw13 {
            display: none !important;
        }
        
        /* Supprimer tout le bloc en haut à droite */
        .stApp > header {
            display: none !important;
        }
        
        /* === BOUTON MANAGE APP EN BAS A DROITE === */
        .stAppViewBlockContainer + div,
        [data-testid="manage-app-button"],
        .streamlit-footer,
        div[class*="StatusWidget"],
        div[class*="stStatusWidget"],
        .reportview-container .main footer,
        iframe[title="streamlit_status"],
        ._container_gzau3_1,
        ._link_gzau3_10,
        ._container_1iGyS_1,
        a[href*="streamlit.io"],
        div:has(> a[href*="streamlit.io"]) {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Cibler specifiquement le bouton Manage app de Streamlit Cloud */
        .st-emotion-cache-1pbsqtx,
        .st-emotion-cache-1egp75f,
        div[data-testid="stBottom"],
        div[data-testid="stBottomBlockContainer"],
        .stBottom,
        [class*="stBottom"] {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Position fixe en bas a droite - Streamlit Cloud */
        div[style*="position: fixed"][style*="bottom"],
        div[style*="position: fixed"][style*="right"] {
            display: none !important;
        }
        
        /* FORCE: Cacher tout element fixe en bas */
        body > div:last-child,
        #root > div:last-child > div:last-child,
        .main + div,
        div[class*="Block"]:last-child {
            /* Ne pas cacher si c'est le contenu principal */
        }
        
        /* Streamlit Cloud Manage App Button - FORCE */
        iframe[title*="Manage"],
        div:has(> iframe[title*="Manage"]),
        [title*="Manage app"],
        a[title*="Manage app"],
        button[title*="Manage app"],
        *[aria-label*="Manage app"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
            width: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
        }
        
        /* === STYLES LOGIN === */
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 40px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h1 {
            color: #333;
            font-size: 1.8em;
            margin-bottom: 10px;
        }
        .login-header p {
            color: #666;
            font-size: 0.9em;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 24px;
        }
    </style>
    
    <script>
        // Supprimer le bouton Manage App de Streamlit Cloud
        function hideManageApp() {
            // Chercher tous les elements contenant "Manage app"
            document.querySelectorAll('*').forEach(el => {
                if (el.innerText && el.innerText.includes('Manage app')) {
                    el.style.display = 'none';
                    el.remove();
                }
                if (el.title && el.title.includes('Manage')) {
                    el.style.display = 'none';
                    el.remove();
                }
            });
            // Chercher les iframes
            document.querySelectorAll('iframe').forEach(iframe => {
                if (iframe.title && iframe.title.toLowerCase().includes('manage')) {
                    iframe.parentElement.style.display = 'none';
                }
            });
            // Elements fixes en bas a droite
            document.querySelectorAll('div').forEach(div => {
                const style = window.getComputedStyle(div);
                if (style.position === 'fixed' && 
                    parseInt(style.bottom) < 100 && 
                    parseInt(style.right) < 100) {
                    div.style.display = 'none';
                }
            });
        }
        // Executer au chargement et periodiquement
        hideManageApp();
        setInterval(hideManageApp, 500);
    </script>
    """, unsafe_allow_html=True)
    
    # Container centré
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo et titre
        logo_b64 = get_logo_base64()
        if logo_b64:
            st.markdown(f'''
            <div class="login-header">
                <img src="data:image/png;base64,{logo_b64}" style="height:80px;margin-bottom:15px;">
                <h1>Contrôle Coffre</h1>
                <p>Système d'audit et de contrôle</p>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="login-header">
                <h1>🍗 KFC Contrôle Coffre</h1>
                <p>Système d'audit et de contrôle</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Formulaire de connexion uniquement
        show_login_form()

def show_login_form():
    """Formulaire de connexion"""
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="votre@email.com")
        password = st.text_input("🔒 Mot de passe", type="password", placeholder="••••••••")
        
        submit = st.form_submit_button("Se connecter", use_container_width=True, type="primary")
        
        if submit:
            if email and password:
                # Compte admin principal (toujours accessible)
                if email == "abrahimatimera@gmail.com" and password == "Banshee1113@":
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_role = "admin"
                    st.success("✅ Connexion réussie!")
                    st.rerun()
                    return
                
                # Vérifier si l'utilisateur existe dans Firebase Auth
                db = firebase_config.init_firebase()
                if db:
                    # Vérifier si l'email existe dans Firebase Auth
                    user = firebase_config.verify_auth_user(email, password)
                    if user:
                        # L'utilisateur existe, on vérifie le mot de passe via Firestore
                        firestore_user = firebase_config.get_user(db, email)
                        if firestore_user and firestore_user.get('password_hash') == hash_password(password):
                            st.session_state.authenticated = True
                            st.session_state.user_email = email
                            st.session_state.user_role = firestore_user.get('role', 'user')
                            st.success("✅ Connexion réussie!")
                            st.rerun()
                        else:
                            # Utilisateur dans Firebase Auth mais pas dans Firestore
                            # On accepte la connexion car créé via le panel admin
                            st.session_state.authenticated = True
                            st.session_state.user_email = email
                            st.session_state.user_role = 'user'
                            st.success("✅ Connexion réussie!")
                            st.rerun()
                    else:
                        st.error("❌ Email ou mot de passe incorrect")
                else:
                    st.error("❌ Connexion à la base de données impossible")
            else:
                st.warning("⚠️ Veuillez remplir tous les champs")

def show_register_form():
    """Formulaire d'inscription"""
    with st.form("register_form"):
        new_email = st.text_input("📧 Email", placeholder="votre@email.com", key="reg_email")
        new_password = st.text_input("🔒 Mot de passe", type="password", placeholder="Min. 6 caractères", key="reg_pass")
        confirm_password = st.text_input("🔒 Confirmer le mot de passe", type="password", placeholder="••••••••", key="reg_confirm")
        
        submit = st.form_submit_button("S'inscrire", use_container_width=True, type="primary")
        
        if submit:
            if new_email and new_password and confirm_password:
                if len(new_password) < 6:
                    st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
                elif new_password != confirm_password:
                    st.error("❌ Les mots de passe ne correspondent pas")
                else:
                    db = firebase_config.init_firebase()
                    if db:
                        # Vérifier si l'utilisateur existe déjà
                        existing_user = firebase_config.get_user(db, new_email)
                        if existing_user:
                            st.error("❌ Cet email est déjà utilisé")
                        else:
                            # Créer l'utilisateur
                            success = firebase_config.add_user(db, new_email, hash_password(new_password))
                            if success:
                                st.success("✅ Compte créé! Vous pouvez maintenant vous connecter.")
                            else:
                                st.error("❌ Erreur lors de la création du compte")
                    else:
                        st.warning("⚠️ Firebase non configuré. Utilisez le compte démo.")
            else:
                st.warning("⚠️ Veuillez remplir tous les champs")

def show_logout_button():
    """Affiche le bouton de déconnexion dans la sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"👤 **{st.session_state.user_email}**")
        if st.session_state.get('user_role') == 'admin':
            st.markdown("🔑 *Administrateur*")
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_role = None
            st.rerun()

def is_admin():
    """Vérifie si l'utilisateur connecté est admin"""
    return st.session_state.get('user_role') == 'admin'

def require_auth(func):
    """Décorateur pour protéger une fonction avec authentification"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('authenticated', False):
            show_login_page()
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def show_admin_panel():
    """Affiche le panneau d'administration (réservé aux admins)"""
    if st.session_state.get('user_role') != 'admin':
        return
    
    with st.expander("🔧 Panneau Administration"):
        st.markdown("### Gestion des utilisateurs")
        
        db = firebase_config.init_firebase()
        
        if db:
            # Liste des utilisateurs Firebase Authentication
            users = firebase_config.list_auth_users()
            
            if users:
                import pandas as pd
                df_users = pd.DataFrame(users)
                cols_display = ['email', 'display_name', 'disabled']
                st.dataframe(df_users[cols_display], use_container_width=True)
                
                st.markdown("---")
                st.markdown("**➕ Créer un nouvel utilisateur**")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_email = st.text_input("Email", placeholder="email@exemple.com", key="new_user_email")
                with col2:
                    new_name = st.text_input("Nom (optionnel)", placeholder="Jean Dupont", key="new_user_name")
                
                new_password = st.text_input("Mot de passe", type="password", placeholder="Min. 6 caractères", key="new_user_pass")
                
                if st.button("✅ Créer l'utilisateur", use_container_width=True):
                    if new_email and new_password:
                        if len(new_password) >= 6:
                            result = firebase_config.create_auth_user(new_email, new_password, new_name if new_name else None)
                            if result == "exists":
                                st.error("❌ Cet email est déjà utilisé")
                            elif result:
                                st.success(f"✅ Utilisateur {new_email} créé avec succès!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la création")
                        else:
                            st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
                    else:
                        st.warning("⚠️ Email et mot de passe requis")
                
                st.markdown("---")
                st.markdown("**🗑️ Supprimer un utilisateur**")
                
                user_options = {u['email']: u['uid'] for u in users if u['email'] != st.session_state.user_email}
                if user_options:
                    user_to_delete = st.selectbox("Utilisateur à supprimer", list(user_options.keys()), key="admin_delete_select")
                    
                    if st.button("🗑️ Supprimer", type="secondary", use_container_width=True):
                        uid = user_options[user_to_delete]
                        if firebase_config.delete_auth_user(uid):
                            st.success(f"✅ Utilisateur {user_to_delete} supprimé")
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de la suppression")
                else:
                    st.info("Aucun autre utilisateur à supprimer")
            else:
                st.info("Aucun utilisateur enregistré dans Firebase Authentication.")
                
                st.markdown("---")
                st.markdown("**➕ Créer le premier utilisateur**")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_email = st.text_input("Email", placeholder="email@exemple.com", key="first_user_email")
                with col2:
                    new_name = st.text_input("Nom (optionnel)", placeholder="Jean Dupont", key="first_user_name")
                
                new_password = st.text_input("Mot de passe", type="password", placeholder="Min. 6 caractères", key="first_user_pass")
                
                if st.button("✅ Créer l'utilisateur", use_container_width=True, key="create_first_user"):
                    if new_email and new_password:
                        if len(new_password) >= 6:
                            result = firebase_config.create_auth_user(new_email, new_password, new_name if new_name else None)
                            if result == "exists":
                                st.error("❌ Cet email est déjà utilisé")
                            elif result:
                                st.success(f"✅ Utilisateur {new_email} créé avec succès!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la création")
                        else:
                            st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
                    else:
                        st.warning("⚠️ Email et mot de passe requis")
        else:
            st.warning("⚠️ Firebase non configuré. Panel admin indisponible en mode démo.")
