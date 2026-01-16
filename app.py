import streamlit as st
import logic
import datetime

# Page config
st.set_page_config(page_title="Café Arcelor", page_icon="☕", layout="centered")

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

def login():
    st.title("☕ Café Arcelor - Connexion")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")
        
        if submitted:
            user = logic.verify_user(email, password)
            if user:
                st.session_state.logged_in = True
                # user = (id, is_admin, valid_until)
                st.session_state.user = {
                    'id': user[0], 
                    'is_admin': bool(user[1]), 
                    'valid_until': user[2],
                    'email': email # On garde l'email pour l'affichage
                }
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect.")

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

def user_view():
    st.title(f"Bonjour {st.session_state.user['email']}")
    st.subheader("☕ Mon Abonnement Café")
    
    # On pourrait recharger l'info depuis la DB pour être sûr d'être à jour
    # Mais pour l'utilisateur simple, la session suffit.
    # Pour être précis, on va simuler un refresh rapide si on voulait, 
    # mais ici on utilise ce qu'on a stocké au login.
    
    valid_until_str = st.session_state.user['valid_until']
    valid_msg = "Pas d'abonnement actif."
    can_drink = False
    
    if valid_until_str:
        try:
            valid_until = datetime.datetime.strptime(valid_until_str, '%Y-%m-%d').date()
            today = datetime.date.today()
            remaining = (valid_until - today).days
            
            if remaining >= 0:
                valid_msg = f"Valide jusqu'au **{valid_until.strftime('%d/%m/%Y')}**\n\n(Il vous reste **{remaining}** jours)"
                can_drink = True
            else:
                valid_msg = f"Expiré depuis le **{valid_until.strftime('%d/%m/%Y')}**"
        except ValueError:
             valid_msg = "Erreur de format de date."
    
    # Affichage visuel fort
    if can_drink:
        st.success(valid_msg)
        st.balloons()
        st.header("✅ Vous pouvez prendre un café !")
    else:
        st.error(valid_msg)
        st.header("❌ Abonnement expiré. Veuillez voir l'administrateur.")

    with st.expander("Changer mon mot de passe"):
        with st.form("change_pwd_user"):
            new_p1 = st.text_input("Nouveau mot de passe", type="password")
            new_p2 = st.text_input("Confirmer mot de passe", type="password")
            if st.form_submit_button("Mettre à jour"):
                if new_p1 and new_p1 == new_p2:
                    if logic.update_password(st.session_state.user['id'], new_p1):
                        st.success("Mot de passe mis à jour !")
                else:
                    st.error("Les mots de passe ne correspondent pas.")

    st.button("Se déconnecter", on_click=logout)

def admin_view():
    st.title("☕ Administration Café Arcelor")
    # Sidebar - Settings
    with st.sidebar.expander("Paramètres Compte"):
        with st.form("change_pwd"):
            new_p1 = st.text_input("Nouveau mot de passe", type="password")
            new_p2 = st.text_input("Confirmer mot de passe", type="password")
            if st.form_submit_button("Changer le mot de passe"):
                if new_p1 and new_p1 == new_p2:
                    if logic.update_password(st.session_state.user['id'], new_p1):
                        st.success("Mot de passe mis à jour !")
                else:
                    st.error("Les mots de passe ne correspondent pas.")

    st.sidebar.text(f"Admin: {st.session_state.user['email']}")
    if st.sidebar.button("Se déconnecter"):
        logout()
    

    tab1, tab2, tab3, tab4 = st.tabs(["Gestion Abonnements", "État Abonnements", "Gestion Stock", "Statistiques"])
    
    with tab1:
        st.header("Gestion Utilisateurs")
        
        # Section Création
        with st.expander("Créer un nouvel utilisateur"):
            with st.form("create_user"):
                new_email = st.text_input("Email nouvel utilisateur")
                new_pwd = st.text_input("Mot de passe par défaut")
                if st.form_submit_button("Créer Compte"):
                    if new_email and new_pwd:
                        if logic.create_user(new_email, new_pwd):
                            st.success(f"Utilisateur {new_email} créé avec succès.")
                            st.rerun()
                        else:
                            st.error("Erreur : Cet email existe déjà.")
                    else:
                        st.warning("Veuillez remplir tous les champs.")

        st.subheader("Ajouter du crédit (Paquet)")
        # List users
        users = logic.get_all_users()
        if users:
            # Format: ID -> "Email (Validité)"
            user_options = {u[0]: f"{u[1]} (Fin : {u[2] if u[2] else 'Aucun'})" for u in users}
            selected_user_id = st.selectbox(
                "Sélectionner un utilisateur pour gérer", 
                options=list(user_options.keys()), 
                format_func=lambda x: user_options[x]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Ajouter 21 jours (+1 paquet)", type="primary"):
                    new_date = logic.add_subscription(selected_user_id)
                    if new_date:
                        st.success(f"Abonnement prolongé jusqu'au {new_date}")
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Erreur mise à jour.")
            
            with col2:
                # Delete button with confirmation (simulated with session state or just direct for now, maybe use checkbox/double click)
                # Streamlit standard: simple button
                if st.button("🗑️ Supprimer l'utilisateur"):
                    logic.delete_user(selected_user_id)
                    st.warning(f"Utilisateur supprimé.")
                    import time
                    time.sleep(1)
                    st.rerun()

        else:
            st.info("Aucun utilisateur standard trouvé.")

    with tab2:
        st.header("État des Abonnements")
        users = logic.get_all_users()
        if users:
            data = []
            today = datetime.date.today()
            
            for u in users:
                user_email = u[1]
                valid_until_str = u[2]
                status_color = "🔴" # Expired default
                days_remaining = -1
                
                if valid_until_str:
                    try:
                        valid_until = datetime.datetime.strptime(valid_until_str, '%Y-%m-%d').date()
                        days_remaining = (valid_until - today).days
                        
                        if days_remaining > 3:
                            status_color = "🟢" # OK
                        elif days_remaining >= 0:
                            status_color = "🟠" # Warning
                        else:
                            status_color = "🔴" # Expired
                    except ValueError:
                        pass
                
                data.append({
                    "Statut": status_color,
                    "Email": user_email,
                    "Expire le": valid_until_str if valid_until_str else "Jamais",
                    "Jours Restants": days_remaining if days_remaining >= 0 else 0
                })
            
            # Display nicely
            st.dataframe(
                data, 
                column_config={
                    "Statut": st.column_config.TextColumn("État", width="small"),
                    "Jours Restants": st.column_config.ProgressColumn(
                        "Validité", 
                        help="Jours restants", 
                        format="%d jours", 
                        min_value=0, 
                        max_value=21,
                    ),
                },
                hide_index=True,
                use_container_width=True
            )
            
            st.caption("🟢 > 3 jours | 🟠 ≤ 3 jours | 🔴 Expiré")
        else:
            st.info("Aucun utilisateur.")

    with tab3:
        st.header("Gestion du Stock")
        
        st.info("Cliquez ci-dessous quand vous ouvrez un nouveau paquet pour la machine.")
        if st.button("📦 Ouvrir un NOUVEAU paquet de café", use_container_width=True, type="primary"):
            logic.log_event('bag_opened')
            st.toast("Ouverture de paquet enregistrée !", icon="✅")
            st.success("Log ajouté : Paquet ouvert.")
            
        st.divider()
        st.subheader("Relevé Compteur Machine")
        counter = st.number_input("Valeur du compteur", min_value=0, step=1)
        if st.button("Enregistrer Relevé"):
            logic.log_event('counter_reading', counter)
            st.success("Relevé enregistré.")

    with tab4:
        st.header("Statistiques")
        df = logic.get_logs_dataframe()
        if not df.empty:
            # Stats packets
            st.subheader("Paquets ouverts par Semaine")
            packets = df[df['event_type'] == 'bag_opened'].copy()
            if not packets.empty:
                # Group by week
                packets['week'] = packets['timestamp'].dt.to_period('W').astype(str)
                counts = packets['week'].value_counts().sort_index()
                st.bar_chart(counts)
            else:
                st.info("Pas encore d'ouverture de paquets enregistrée.")
                
            with st.expander("Voir les données brutes"):
                st.dataframe(df)
        else:
            st.info("Aucune donnée disponible pour le moment.")

# Router
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.user['is_admin']:
        admin_view()
    else:
        user_view()
