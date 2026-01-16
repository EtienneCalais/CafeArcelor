import sqlite3
import hashlib
import datetime
import pandas as pd
from db import get_connection

def verify_user(email, password):
    """Vérifie les identifiants et retourne les infos utilisateur."""
    conn = get_connection()
    c = conn.cursor()
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute('SELECT id, is_admin, valid_until FROM users WHERE email = ? AND password = ?', (email, pwd_hash))
    user = c.fetchone()
    conn.close()
    return user # (id, is_admin, valid_until)

def add_subscription(user_id):
    """Ajoute 21 jours d'abonnement selon les règles métier."""
    conn = get_connection()
    c = conn.cursor()
    
    # Récupérer la validité actuelle
    c.execute('SELECT valid_until FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    
    if result:
        current_valid_until_str = result[0]
        today = datetime.date.today()
        
        if current_valid_until_str:
            try:
                current_valid_until = datetime.datetime.strptime(current_valid_until_str, '%Y-%m-%d').date()
                if current_valid_until < today:
                    # Abonnement expiré : on repart d'aujourd'hui
                    new_date = today + datetime.timedelta(days=21)
                else:
                    # Abonnement actif : on ajoute à la fin
                    new_date = current_valid_until + datetime.timedelta(days=21)
            except ValueError:
                # Si format de date invalide en base, on repart d'aujourd'hui
                new_date = today + datetime.timedelta(days=21)
        else:
            # Jamais abonné
            new_date = today + datetime.timedelta(days=21)
            
        c.execute('UPDATE users SET valid_until = ? WHERE id = ?', (new_date, user_id))
        conn.commit()
        conn.close()
        return new_date
    conn.close()
    return None

def log_event(event_type, value=None):
    """Log un événement (ouverture de paquet, relevé compteur)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO stock_logs (event_type, machine_counter_value) VALUES (?, ?)', (event_type, value))
    conn.commit()
    conn.close()

def get_all_users():
    """Récupère tous les utilisateurs non-admin."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, email, valid_until FROM users WHERE is_admin = 0')
    users = c.fetchall()
    conn.close()
    return users

def create_user(email, password):
    """Crée un nouvel utilisateur standard."""
    conn = get_connection()
    c = conn.cursor()
    try:
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute('INSERT INTO users (email, password, is_admin) VALUES (?, ?, 0)', (email, pwd_hash))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # Email déjà existant
    conn.close()
    return success

def delete_user(user_id):
    """Supprime un utilisateur par son ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

def update_password(user_id, new_password):
    """Met à jour le mot de passe d'un utilisateur."""
    conn = get_connection()
    c = conn.cursor()
    new_hash = hashlib.sha256(new_password.encode()).hexdigest()
    c.execute('UPDATE users SET password = ? WHERE id = ?', (new_hash, user_id))
    conn.commit()
    conn.close()
    return True

def get_logs_dataframe():
    """Récupère les logs pour l'analyse via Pandas."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM stock_logs", conn)
    conn.close()
    # Convertir timestamp en datetime
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df
