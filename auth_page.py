import streamlit as st
import hashlib
import firebase_config

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
    
    # CSS pour la page de connexion
    st.markdown("""
    <style>
        /* Cacher le menu Manage App sur la page de connexion */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stToolbar"] {visibility: hidden;}
        [data-testid="manage-app-button"] {display: none;}
        
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
    """, unsafe_allow_html=True)
    
    # Container centré
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo et titre
        st.markdown("""
        <div class="login-header">
            <h1>🍗 KFC Contrôle Coffre</h1>
            <p>Système d'audit et de contrôle</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Onglets Connexion / Inscription
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            show_login_form()
        
        with tab2:
            show_register_form()

def show_login_form():
    """Formulaire de connexion"""
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="votre@email.com")
        password = st.text_input("🔒 Mot de passe", type="password", placeholder="••••••••")
        
        submit = st.form_submit_button("Se connecter", use_container_width=True, type="primary")
        
        if submit:
            if email and password:
                # Vérifier les credentials
                db = firebase_config.init_firebase()
                if db:
                    user = firebase_config.get_user(db, email)
                    if user and user.get('password_hash') == hash_password(password):
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_role = user.get('role', 'user')
                        st.success("✅ Connexion réussie!")
                        st.rerun()
                    else:
                        st.error("❌ Email ou mot de passe incorrect")
                else:
                    # Mode démo sans Firebase
                    if email == "demo@kfc.com" and password == "demo123":
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_role = "admin"
                        st.success("✅ Connexion réussie (mode démo)!")
                        st.rerun()
                    else:
                        st.error("❌ Email ou mot de passe incorrect")
            else:
                st.warning("⚠️ Veuillez remplir tous les champs")
    
    # Compte démo
    st.markdown("---")
    st.info("**Mode démo:** demo@kfc.com / demo123")

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
            # Liste des utilisateurs
            users_ref = db.collection('users')
            users = [doc.to_dict() | {'id': doc.id} for doc in users_ref.stream()]
            
            if users:
                import pandas as pd
                df_users = pd.DataFrame(users)
                cols_display = ['email', 'role', 'created_at'] if 'created_at' in df_users.columns else ['email', 'role']
                st.dataframe(df_users[cols_display], use_container_width=True)
                
                st.markdown("---")
                st.markdown("**Modifier le rôle d'un utilisateur**")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    user_emails = [u['email'] for u in users]
                    selected_user = st.selectbox("Utilisateur", user_emails, key="admin_user_select")
                
                with col2:
                    new_role = st.selectbox("Nouveau rôle", ["user", "admin", "manager"], key="admin_role_select")
                
                with col3:
                    if st.button("✅ Modifier", use_container_width=True):
                        users_ref.document(selected_user).update({'role': new_role})
                        st.success(f"Rôle de {selected_user} modifié en {new_role}")
                        st.rerun()
                
                st.markdown("---")
                st.markdown("**Supprimer un utilisateur**")
                
                col_d1, col_d2 = st.columns([2, 1])
                with col_d1:
                    user_to_delete = st.selectbox("Utilisateur à supprimer", user_emails, key="admin_delete_select")
                with col_d2:
                    if st.button("🗑️ Supprimer", type="secondary", use_container_width=True):
                        if user_to_delete != st.session_state.user_email:
                            users_ref.document(user_to_delete).delete()
                            st.success(f"Utilisateur {user_to_delete} supprimé")
                            st.rerun()
                        else:
                            st.error("Vous ne pouvez pas supprimer votre propre compte!")
            else:
                st.info("Aucun utilisateur enregistré.")
        else:
            st.warning("⚠️ Firebase non configuré. Panel admin indisponible en mode démo.")
