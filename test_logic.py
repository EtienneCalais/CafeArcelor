import logic
import db
import datetime
import os

def test():
    print("Début des Tests Logique...")
    
    # 1. Création Utilisateur Test
    email = "test_auto@arcelor.com"
    pwd = "123"
    
    # Nettoyage préalable
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE email=?", (email,))
    conn.commit()
    conn.close()
    
    created = logic.create_user(email, pwd)
    print(f"Utilisateur créé : {created}")
    assert created == True
    
    user = logic.verify_user(email, pwd)
    print(f"Utilisateur vérifié : {user}")
    assert user is not None
    user_id = user[0]
    
    # 2. Ajout Abonnement (Premier - Date du jour + 21)
    new_date = logic.add_subscription(user_id)
    print(f"Abonnement 1 (Nouveau) : {new_date}")
    expected_date = datetime.date.today() + datetime.timedelta(days=21)
    assert new_date == expected_date
    
    # 3. Ajout Abonnement (Extension - Validité précédente + 21)
    new_date_2 = logic.add_subscription(user_id)
    print(f"Abonnement 2 (Extension) : {new_date_2}")
    expected_date_2 = new_date + datetime.timedelta(days=21)
    assert new_date_2 == expected_date_2
    
    # 4. Logs
    logic.log_event("test_event", 999)
    df = logic.get_logs_dataframe()
    print("Dernier log :")
    print(df.tail(1))
    assert not df[df['machine_counter_value'] == 999].empty
    
    print("✅ TOUS LES TESTS SONT PASSÉS")

if __name__ == "__main__":
    test()
