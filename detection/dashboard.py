"""
Dashboard de détection d'anomalies en temps réel (Streamlit).
Interface graphique permettant de démarrer/arrêter la détection,
de visualiser les alertes (Ransomware, Burst, etc.), d'afficher 
les détails techniques et de tracer l'évolution du score d'anomalie.
"""
from collections import deque
import real_time_detecteur as rd
from watchdog.observers import Observer
import streamlit as st
import time  
import threading
import plotly.graph_objects as go


# Variable globale pour le thread
detection_active_thread = False
st.set_page_config(page_title="Détection d'Anomalies",layout="wide")

# initialisation
if 'buffer_evenements' not in st.session_state:
    st.session_state.buffer_evenements=deque(maxlen=10000)
    rd.buffer_evenements = st.session_state.buffer_evenements
    st.session_state.historique_alertes=[]
    st.session_state.detection_active=False
    st.session_state.observateur=None
    st.session_state.compteur_analyses=0
    #pour les graphes
    st.session_state.historique_scores=[]  
    st.session_state.historique_timestamps=[]

# initialisation
def boucle_collecte():
    global detection_active_thread
    while detection_active_thread:
        try:
            rd.collecter_systeme()
            rd.collecter_processus()
            rd.collecter_reseau()
            time.sleep(2)
        except Exception as e:
            print(f"Erreur: {e}")

def demarrer():
    global detection_active_thread
    if not st.session_state.detection_active:
        st.session_state.detection_active=True
        detection_active_thread = True
        st.session_state.observateur=Observer()
        st.session_state.observateur.schedule(rd.CollecteurFichier(), path="/tmp",recursive=True)
        st.session_state.observateur.start()
        threading.Thread(target=boucle_collecte,daemon=True).start()

def arreter():
    global detection_active_thread
    if st.session_state.detection_active:
        st.session_state.detection_active=False
        detection_active_thread = False
        if st.session_state.observateur:
            st.session_state.observateur.stop()

# dashboard
st.title("Détecteur d'anomalies en temps réel")
col1, col2, col3, col4 = st.columns([1, 1,2,2])
with col1:
    if st.button("▶️ Démarrer",use_container_width=True):
        demarrer()
        st.rerun()
with col2:
    if st.button("⏹️ Arrêter",use_container_width=True):
        arreter()
        st.rerun()

with col3:
    if st.session_state.detection_active:
        st.success("détection active")
    else:
        st.error("détection inactive")

with col4:
    st.info(f"Buffer:{len(st.session_state.buffer_evenements)} événements")

st.markdown("---")

#si la detection est active
if st.session_state.detection_active:
    # Zone de statut (mise à jour en direct)
    status_zone=st.empty()
    details_zone=st.empty()
    alertes_zone=st.empty()
    # Boucle de détection
    for _ in range(100):
        if not st.session_state.detection_active:
            break
        try:
            # Prédiction
            resultat = rd.predire_anomalie()
            st.session_state.compteur_analyses+=1
            # Mettre à jour l'historique pour les graphiques
            st.session_state.historique_scores.append(resultat['score'])
            st.session_state.historique_timestamps.append(resultat['timestamp'])
            # Garder seulement les 20 dernières valeurs
            if len(st.session_state.historique_scores)>20:
                st.session_state.historique_scores.pop(0)
                st.session_state.historique_timestamps.pop(0)
            # Affichage du statut principal 
            with status_zone.container():
                if resultat["status"]=="SUSPECT":
                    st.error(f"""
                    # Alerte detctée
                    -Type d'attaque:{resultat['type_anomalie']}  
                    -Score de confiance : {resultat['score']:.1%}  
                    -Heure : {resultat['timestamp']}
                    """)
                    # Ajouter à l'historique
                    st.session_state.historique_alertes.append(resultat)
                else:
                    st.success(f"""
                    # Système Normal
                    -Score de soupçon : {resultat['score']:.1%}  
                    -Analyses effectuées : {st.session_state.compteur_analyses}  
                    -Heure : {resultat['timestamp']}
                    """)
            
            # Détails techniques seulement si suspect 
            with details_zone.container():
                if resultat["status"]=="SUSPECT":
                    st.subheader("Détails de l'Anomalie")
                    col1, col2, col3=st.columns(3)
                    with col1:
                        st.markdown("Fichiers")
                        st.write(f"Créés: {resultat['features']['nombre_fichiers_crees']}")
                        st.write(f"Supprimés: {resultat['features']['nombre_fichiers_supprimes']}")
                        st.write(f"Modifiés: {resultat['features']['nombre_fichiers_modifies']}")
                    with col2:
                        st.markdown("Processus")
                        st.write(f"CPU Max: {resultat['features']['max_cpu']:.1f}%")
                        st.write(f"CPU Moyen: {resultat['features']['moyenne_cpu']:.1f}%")
                        st.write(f"Threads: {resultat['features']['max_threads']}") 
                    with col3:
                        st.markdown("Réseau")
                        st.write(f"Connexions: {resultat['features']['max_connexions_simultanees']}")
                        st.write(f"Ports: {resultat['features']['nombre_ports_distincts']}")
                        st.write(f"IPs: {resultat['features']['nombre_ip_distinctes']}")
            with alertes_zone.container():
                # 2 graphes en 2 colonnes
                st.markdown("---")
                col_graph1, col_graph2 = st.columns(2)
                # Courbe d'évolution du score
                with col_graph1:
                    if len(st.session_state.historique_scores) > 1:
                        st.subheader("Évolution du Score")
                        fig_line = go.Figure()
                        fig_line.add_trace(go.Scatter(
                            x=st.session_state.historique_timestamps,
                            y=st.session_state.historique_scores,
                            mode='lines+markers',
                            name='Score',
                            line=dict(color='rgb(31, 119, 180)', width=2),
                            marker=dict(size=6)
                        ))
                        fig_line.add_hline(y=0.5,line_dash="dash", line_color="red",annotation_text="Seuil (50%)")
                        fig_line.update_layout(
                            xaxis_title="Heure",
                            yaxis_title="Score",
                            yaxis_range=[0,1],
                            height=300,
                            margin=dict(l=20,r=20,t=20,b=20)
                        )
                        st.plotly_chart(fig_line,use_container_width=True,key=f"score_line_{st.session_state.compteur_analyses}")
                
                #Pie chart des types d'événements
                with col_graph2:
                    if len(st.session_state.buffer_evenements)>0:
                        st.subheader("Répartition des Événements")
                        buffer_copy=list(st.session_state.buffer_evenements)
                        # Compter les événements par type
                        type_file=0
                        type_process=0
                        type_network=0
                        type_system=0
                        for evt in buffer_copy:
                            evt_type=evt['data'].get('type', '')
                            if evt_type=='file':
                                type_file+=1
                            elif evt_type=='process':
                                type_process+=1
                            elif evt_type=='network':
                                type_network+=1
                            elif evt_type=='system':
                                type_system+=1
                        # Créer le pie chart
                        fig_pie = go.Figure(data=[go.Pie(
                            labels=['Fichiers','Processus','Réseau','Système'],
                            values=[type_file, type_process, type_network, type_system],
                            hole=0.3,
                            marker=dict(colors=['#FF6B6B','#4ECDC4','#45B7D1','#FFA07A'])
                        )])
                        fig_pie.update_layout(
                            height=300,
                            margin=dict(l=20,r=20,t=20,b=20),
                            showlegend=True
                        )
                        st.plotly_chart(fig_pie,use_container_width=True,key=f"event_pie_{st.session_state.compteur_analyses}")
                
                #historique des alertes
                st.markdown("---")
                if st.session_state.historique_alertes:
                    st.subheader(f"Historique des Alertes ({len(st.session_state.historique_alertes)})")
                    # Tableau simple
                    for i, alerte in enumerate(reversed(st.session_state.historique_alertes[-10:]), 1):
                        st.warning(f"""
                        Alerte #{len(st.session_state.historique_alertes)-i+1}-[{alerte['timestamp']}]  
                        Type: {alerte['type_anomalie']} | Score: {alerte['score']:.1%}
                        """)
        
        except Exception as e:
            st.error(f"Erreur: {e}")
        
        time.sleep(3)
    
    st.rerun()

else:
    st.info("""Cliquez sur "Démarrer" pour lancer la détection""")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Types d'Attaques Détectées")
        st.markdown("""
        -Ransomware : Chiffrement massif de fichiers
        -Scan Réseau : Balayage de ports
        -Keylogger : Lecture répétée de fichiers
        -Exfiltration : Transfert de données massif
        -Brute Force : Multiples tentatives d'accès
        -Burst : Création/suppression rapide de fichiers
        """)
    with col2:
        st.subheader("Performance du Modèle")
        st.markdown("""
        -Modèle : XGBoost  
        -Précision : 99.1%  
        -Features : 21  
        -Fenêtre d'analyse : 10 secondes  
        -Fréquence de prédiction : Toutes les 3 secondes
        """)
        if st.session_state.historique_alertes:
            st.metric("Alertes détectées",len(st.session_state.historique_alertes))

