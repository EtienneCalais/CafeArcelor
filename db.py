import sqlite3
import hashlib

DB_NAME = 'cafe_arcelor.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Users table
    # valid_until stocke la date au format YYYY-MM-DD
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            valid_until DATE
        )
    ''')
    
    # Stock logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            machine_counter_value INTEGER
        )
    ''')
    
    # Check for admin
    c.execute('SELECT * FROM users WHERE email = ?', ('admin@arcelor.com',))
    if not c.fetchone():
        # Create default admin
        # Hachage simple SHA256 pour la démo
        pwd_hash = hashlib.sha256('admin'.encode()).hexdigest()
        c.execute('INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)',
                  ('admin@arcelor.com', pwd_hash, True))
        print("Admin user created (admin@arcelor.com / admin).")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
