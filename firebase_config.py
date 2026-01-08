import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
import os

def init_firebase():
    """Initialise la connexion Firebase"""
    try:
        # Vérifier si Firebase est déjà initialisé
        if not firebase_admin._apps:
            # Option 1: Utiliser les secrets Streamlit (pour déploiement)
            if hasattr(st, 'secrets') and 'firebase' in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                cred = credentials.Certificate(cred_dict)
            # Option 2: Utiliser un fichier local (pour développement)
            elif os.path.exists("firebase_credentials.json"):
                cred = credentials.Certificate("firebase_credentials.json")
            else:
                st.error("⚠️ Configuration Firebase manquante!")
                st.info("""
                Pour configurer Firebase:
                1. Créez un projet sur https://console.firebase.google.com
                2. Allez dans Paramètres > Comptes de service
                3. Générez une nouvelle clé privée
                4. Sauvegardez le fichier JSON comme 'firebase_credentials.json'
                """)
                return None
            
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    
    except Exception as e:
        st.error(f"Erreur Firebase: {str(e)}")
        return None

def get_users_collection(db):
    """Retourne la collection des utilisateurs"""
    if db:
        return db.collection('users')
    return None

def add_user(db, email, password_hash, role="user"):
    """Ajoute un utilisateur dans Firestore"""
    users_ref = get_users_collection(db)
    if users_ref:
        users_ref.document(email).set({
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return True
    return False

def get_user(db, email):
    """Récupère un utilisateur par email"""
    users_ref = get_users_collection(db)
    if users_ref:
        doc = users_ref.document(email).get()
        if doc.exists:
            return doc.to_dict()
    return None

def save_audit(db, audit_data, user_email):
    """Sauvegarde un audit dans Firestore"""
    if db:
        audits_ref = db.collection('audits')
        audit_data['user_email'] = user_email
        audit_data['timestamp'] = firestore.SERVER_TIMESTAMP
        audits_ref.add(audit_data)
        return True
    return False

def get_audits(db, user_email=None):
    """Récupère les audits (tous ou par utilisateur)"""
    if db:
        audits_ref = db.collection('audits')
        if user_email:
            docs = audits_ref.where('user_email', '==', user_email).stream()
        else:
            docs = audits_ref.stream()
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    return []

def delete_audit(db, audit_id):
    """Supprime un audit par ID"""
    if db:
        db.collection('audits').document(audit_id).delete()
        return True
    return False
