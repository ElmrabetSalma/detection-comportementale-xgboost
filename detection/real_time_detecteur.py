"""
Détecteur d'anomalies en temps réel.
Charge le modèle XGBoost et les noms de features, collecte les événements 
système (processus, fichiers, réseau), calcule les 21 features sur une fenêtre 
de 10 secondes, prédit si la fenêtre est bénigne ou suspecte, et identifie 
le type d'attaque (Burst, Keylogger, Scan Réseau, etc.).
"""
import joblib
import pandas as pd
import numpy as np
import json
import psutil as ps
from watchdog.events import FileSystemEventHandler 
from datetime import datetime
import time

buffer_evenements = None

# Stocker en mémoire
def stocker_event_memoire(evenement):
    global buffer_evenements  
    if buffer_evenements is not None: 
        buffer_evenements.append({
            'data': evenement.convertir_en_dictionnaire(),
            'timestamp': evenement.timestamp
        })

# Classe par type d'événement  
class evenement_processus:
    def __init__(self, timestamp, type, nom, cmdline, pid, duree_execution, cpu_pourcentage, ram_pourcentage, io_read_bytes, io_write_bytes, nbre_threads, nbre_fils):
        self.timestamp = timestamp
        self.type = type
        self.nom = nom
        self.cmdline = cmdline
        self.pid = pid
        self.duree_execution = duree_execution
        self.cpu_pourcentage = cpu_pourcentage
        self.ram_pourcentage = ram_pourcentage
        self.io_read_bytes = io_read_bytes
        self.io_write_bytes = io_write_bytes
        self.nbre_threads = nbre_threads
        self.nbre_fils = nbre_fils
    def convertir_en_dictionnaire(self):
        return self.__dict__

class evenement_fichier:
    def __init__(self, timestamp, type, chemin, action, est_dossier):
        self.timestamp = timestamp
        self.type = type
        self.chemin = chemin
        self.action = action
        self.est_dossier = est_dossier
    def convertir_en_dictionnaire(self):
        return self.__dict__

class evenement_reseau:
    def __init__(self, timestamp, type, nbre_connexions, unique_ports, unique_ips, bytes_sent):
        self.timestamp = timestamp
        self.type = type
        self.nbre_connexions = nbre_connexions
        self.unique_ports = unique_ports
        self.unique_ips = unique_ips
        self.bytes_sent = bytes_sent
    def convertir_en_dictionnaire(self):
        return self.__dict__

class evenement_systeme:    
    def __init__(self, timestamp, type, cpu_pourcentage, cpu_frequence, ram_pourcentage, swap_pourcentage):
        self.timestamp = timestamp
        self.type = type
        self.cpu_pourcentage = cpu_pourcentage
        self.ram_pourcentage = ram_pourcentage
        self.cpu_frequence = cpu_frequence
        self.swap_pourcentage = swap_pourcentage
    def convertir_en_dictionnaire(self):
        return self.__dict__

# Un collecteur par type d'événement
def collecter_systeme():
    type = "system"
    timestamp = int(time.time() * 1000) # en ms
    cpu_pourcentage = ps.cpu_percent()    # %CPU total
    ram_pourcentage = ps.virtual_memory().percent
    cpu_frequence = ps.cpu_freq().current
    swap_pourcentage = ps.swap_memory().percent
    evenement = evenement_systeme(timestamp, type, cpu_pourcentage, cpu_frequence, ram_pourcentage, swap_pourcentage)  
    stocker_event_memoire(evenement)    

def collecter_processus():
    for p in ps.process_iter():
        try:
            timestamp = int(time.time() * 1000)
            type = "process"
            nom = p.name()
            try:
                cmdline_list = p.cmdline()
                cmdline = ' '.join(cmdline_list)
            except (ps.AccessDenied, ps.ZombieProcess):
                cmdline = "" 
            pid = p.pid
            duree_execution = int((time.time() - p.create_time()) * 1000)
            cpu_pourcentage = p.cpu_percent()
            ram_pourcentage = p.memory_percent()
            try:
                io_counters = p.io_counters() 
                io_read_bytes = io_counters.read_bytes
                io_write_bytes = io_counters.write_bytes
            except (ps.AccessDenied, AttributeError):
                io_read_bytes = 0
                io_write_bytes = 0
            nbre_threads = p.num_threads()
            nbre_fils = len(p.children(recursive=False))
            evenement = evenement_processus(timestamp, type, nom, cmdline, pid, duree_execution, cpu_pourcentage, ram_pourcentage, io_read_bytes, io_write_bytes, nbre_threads, nbre_fils)
            stocker_event_memoire(evenement)
        except (ps.NoSuchProcess, ps.AccessDenied):
                continue

def collecter_reseau():
    timestamp = int(time.time() * 1000)
    type = "network"
    connexions = ps.net_connections(kind='inet')
    nbre_connexions = 0
    ports = set()
    ips = set()
    bytes_sent = ps.net_io_counters().bytes_sent
    for connexion in connexions:
        if connexion.status == 'ESTABLISHED':
            nbre_connexions = nbre_connexions + 1
            if connexion.raddr:
                    ports.add(connexion.raddr.port)
                    if connexion.raddr.ip:  
                        ips.add(connexion.raddr.ip)
            if connexion.laddr:
                    ports.add(connexion.laddr.port)
    unique_ports = list(ports) if ports else []
    unique_ips = list(ips) if ips else []
    evenement = evenement_reseau(timestamp, type, nbre_connexions, unique_ports, unique_ips, bytes_sent)
    stocker_event_memoire(evenement)   

class CollecteurFichier(FileSystemEventHandler):
    def on_modified(self, evenement):
        timestamp = int(time.time() * 1000)
        type = "file"
        chemin = evenement.src_path 
        action = "modify"
        est_dossier = evenement.is_directory 
        evenement = evenement_fichier(timestamp, type, chemin, action, est_dossier)
        stocker_event_memoire(evenement)
    def on_created(self, evenement):
        timestamp = int(time.time() * 1000)
        type = "file"
        chemin = evenement.src_path 
        action = "create"
        est_dossier = evenement.is_directory 
        evenement = evenement_fichier(timestamp, type, chemin, action, est_dossier)
        stocker_event_memoire(evenement)
    def on_deleted(self, evenement):
        timestamp = int(time.time() * 1000)
        type = "file"
        chemin = evenement.src_path 
        action = "delete"
        est_dossier = evenement.is_directory 
        evenement = evenement_fichier(timestamp, type, chemin, action, est_dossier)
        stocker_event_memoire(evenement)

# Calculer features tous les 10s
def calculer_features_fenetre_10s():
    maintenant = int(time.time() * 1000)  # ms
    debut_fenetre = maintenant - 10000    
    evenements_fenetre = [
        e['data'] for e in buffer_evenements 
        if e['timestamp'] >= debut_fenetre
    ]
    
    if len(evenements_fenetre) == 0:
        return {
            "nombre_d_evenements_file": 0, "nombre_fichiers_crees": 0, "nombre_fichiers_supprimes": 0, "nombre_fichiers_modifies": 0,
            "nombre_d_evenements_process": 0, "nombre_d_evenements_network": 0, "nombre_d_evenements_system": 0, "nombre_total_d_evenements": 0,
            "max_connexions_simultanees": 0, "nombre_ports_distincts": 0, "nombre_ip_distinctes": 0, "octets_envoyes": 0, "port_persistence": 0,
            "max_cpu": 0, "moyenne_cpu": 0, "stabilite_cpu": 0, "max_threads": 0, "octets_lus": 0, "octets_ecrits": 0, "rapport_io": 1.0, "fichier_par_seconde": 0
        }
    
    evenements_type_file = [e for e in evenements_fenetre if e['type'] == 'file']
    evenements_type_process = [e for e in evenements_fenetre if e['type'] == 'process']
    evenements_type_network = [e for e in evenements_fenetre if e['type'] == 'network']
    evenements_type_system = [e for e in evenements_fenetre if e['type'] == 'system']
    
    nombre_d_evenements_file = len(evenements_type_file)
    nombre_fichiers_crees = len([e for e in evenements_type_file if e.get('action') == 'create'])
    nombre_fichiers_supprimes = len([e for e in evenements_type_file if e.get('action') == 'delete'])
    nombre_fichiers_modifies = len([e for e in evenements_type_file if e.get('action') == 'modify'])
    nombre_d_evenements_process = len(evenements_type_process)
    nombre_d_evenements_network = len(evenements_type_network)
    nombre_d_evenements_system = len(evenements_type_system)
    nombre_total_d_evenements = len(evenements_fenetre)
    
    if evenements_type_network:
        max_connexions_simultanees = max([e.get('nbre_connexions', 0) for e in evenements_type_network])
        all_ports = []
        for e in evenements_type_network:
            ports = e.get('unique_ports', [])
            if isinstance(ports, list):
                all_ports.extend(ports)
        nombre_ports_distincts = len(set(all_ports))
        all_ips = []
        for e in evenements_type_network:
            ips = e.get('unique_ips', [])
            if isinstance(ips, list):
                all_ips.extend(ips)
        nombre_ip_distinctes = len(set(all_ips))
        bytes_sent_values = [e.get('bytes_sent', 0) for e in evenements_type_network]
        octets_envoyes = max(bytes_sent_values) - min(bytes_sent_values) if len(bytes_sent_values) >= 2 else 0
        if all_ports:
            from collections import Counter
            port_persistence = max(Counter(all_ports).values())
        else:
            port_persistence = 0
    else:
        max_connexions_simultanees = nombre_ports_distincts = nombre_ip_distinctes = octets_envoyes = port_persistence = 0
        
    if evenements_type_process:
        cpu_values = [e.get('cpu_pourcentage', 0) for e in evenements_type_process]
        threads_values = [e.get('nbre_threads', 0) for e in evenements_type_process]
        io_read_values = [e.get('io_read_bytes', 0) for e in evenements_type_process]
        io_write_values = [e.get('io_write_bytes', 0) for e in evenements_type_process]
        max_cpu = max(cpu_values)
        moyenne_cpu = np.mean(cpu_values)
        stabilite_cpu = np.std(cpu_values)
        max_threads = max(threads_values)
        octets_lus = sum(io_read_values)
        octets_ecrits = sum(io_write_values)
    else:
        max_cpu = moyenne_cpu = stabilite_cpu = max_threads = octets_lus = octets_ecrits = 0
        
    rapport_io = (octets_lus + 1) / (octets_ecrits + 1)
    fichier_par_seconde = nombre_fichiers_crees / 10.0
    
    return {
        "nombre_d_evenements_file": nombre_d_evenements_file, "nombre_fichiers_crees": nombre_fichiers_crees, "nombre_fichiers_supprimes": nombre_fichiers_supprimes, "nombre_fichiers_modifies": nombre_fichiers_modifies,
        "nombre_d_evenements_process": nombre_d_evenements_process, "nombre_d_evenements_network": nombre_d_evenements_network, "nombre_d_evenements_system": nombre_d_evenements_system, "nombre_total_d_evenements": nombre_total_d_evenements,
        "max_connexions_simultanees": max_connexions_simultanees, "nombre_ports_distincts": nombre_ports_distincts, "nombre_ip_distinctes": nombre_ip_distinctes, "octets_envoyes": octets_envoyes, "port_persistence": port_persistence,
        "max_cpu": max_cpu, "moyenne_cpu": moyenne_cpu, "stabilite_cpu": stabilite_cpu, "max_threads": max_threads, "octets_lus": octets_lus, "octets_ecrits": octets_ecrits, "rapport_io": rapport_io, "fichier_par_seconde": fichier_par_seconde
    }

# Charger le modèle
modele = joblib.load("modele_final/modele_xgboost.pkl")
noms_features = json.load(open("modele_final/features.json"))

# Calculer les features et prédire si c'est normal ou suspect
def predire_anomalie():
    features_calculees = calculer_features_fenetre_10s()
    df = pd.DataFrame([features_calculees])
    df = df[noms_features]
    prediction = modele.predict(df)[0]
    probabilite = modele.predict_proba(df)[0]
    type_anomalie = identifier_type_anomalie(features_calculees) if prediction == 1 else None
    return {
        "status": "SUSPECT" if prediction == 1 else "BENIN",
        "score": float(probabilite[1]),  
        "features": features_calculees,
        "type_anomalie": type_anomalie,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

def identifier_type_anomalie(features):
    if features["fichier_par_seconde"] > 100:
        return "Burst Fichiers"
    if (features["rapport_io"] < 0.2):
        return "Keylogger"
    if (features["nombre_ports_distincts"] > 50 or features["nombre_ip_distinctes"] > 20):
        return "Scan Réseau"
    if features["octets_envoyes"] > 1000000: 
        return "Exfiltration"
    if (features["max_threads"] > 40 and features["moyenne_cpu"] > 10):
        return "Brute Force"
    return "Anomalie Inconnue"
