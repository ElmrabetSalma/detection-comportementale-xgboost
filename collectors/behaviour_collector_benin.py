"""
Collecteur de comportement bénin (Baseline).
Capture la télémétrie système (processus, fichiers, réseau, CPU/RAM) 
et l'enregistre dans un fichier JSONL (collecte_resultats_benins.jsonl).
Utilisé pour entraîner le modèle à reconnaître l'état normal du système.
"""
import time
import json
import psutil as ps
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

fichier_de_collecte="collecte_resultats_benins.jsonl"
fichier=open(fichier_de_collecte,"a",buffering=1)
def log_event(evenement):
    fichier.write(json.dumps(evenement.convertir_en_dictionnaire())+"\n")
    fichier.flush()
    
class evenement_processus:
    def __init__(self,timestamp,type,nom,cmdline,pid,duree_execution,cpu_pourcentage,ram_pourcentage,io_read_bytes,io_write_bytes,nbre_threads,nbre_fils):
        self.timestamp=timestamp
        self.type=type
        self.nom=nom
        self.cmdline=cmdline
        self.pid=pid
        self.duree_execution=duree_execution
        self.cpu_pourcentage=cpu_pourcentage
        self.ram_pourcentage=ram_pourcentage
        self.io_read_bytes=io_read_bytes
        self.io_write_bytes=io_write_bytes
        self.nbre_threads=nbre_threads
        self.nbre_fils=nbre_fils
    def convertir_en_dictionnaire(self):
        return self.__dict__

class evenement_fichier:
    def __init__(self,timestamp,type,chemin,action,est_dossier):
        self.timestamp=timestamp
        self.type=type
        self.chemin=chemin
        self.action=action
        self.est_dossier=est_dossier
    def convertir_en_dictionnaire(self):
        return self.__dict__

class evenement_reseau:
    def __init__(self,timestamp,type,nbre_connexions,unique_ports,unique_ips,bytes_sent):
        self.timestamp=timestamp
        self.type=type
        self.nbre_connexions=nbre_connexions
        self.unique_ports=unique_ports
        self.unique_ips=unique_ips
        self.bytes_sent=bytes_sent
    def convertir_en_dictionnaire(self):
        return self.__dict__

class evenement_systeme:    #global
    def __init__(self,timestamp,type,cpu_pourcentage,cpu_frequence,ram_pourcentage,swap_pourcentage):
        self.timestamp=timestamp
        self.type=type
        self.cpu_pourcentage=cpu_pourcentage
        self.ram_pourcentage=ram_pourcentage
        self.cpu_frequence=cpu_frequence
        self.swap_pourcentage=swap_pourcentage
    def convertir_en_dictionnaire(self):
        return self.__dict__



def collecter_systeme():
    type="system"
    timestamp=int(time.time()*1000) #en ms
    cpu_pourcentage=ps.cpu_percent()    #%CPU total
    ram_pourcentage=ps.virtual_memory().percent
    cpu_frequence=ps.cpu_freq().current
    swap_pourcentage=ps.swap_memory().percent
    evenement=evenement_systeme(timestamp,type,cpu_pourcentage,cpu_frequence,ram_pourcentage,swap_pourcentage)  
    log_event(evenement)
      
def collecter_processus():
    for p in ps.process_iter():
        try:
            timestamp=int(time.time()*1000)
            type="process"
            nom=p.name()
            
            try:
                cmdline_list=p.cmdline()
                cmdline=' '.join(cmdline_list)
            except (ps.AccessDenied, ps.ZombieProcess):
                cmdline = "" 
            
            pid=p.pid
            duree_execution=int((time.time()-p.create_time())*1000)
            cpu_pourcentage=p.cpu_percent()
            ram_pourcentage=p.memory_percent()
            
            try:
                io_counters=p.io_counters() 
                io_read_bytes=io_counters.read_bytes
                io_write_bytes=io_counters.write_bytes
            except (ps.AccessDenied,AttributeError):
                io_read_bytes=0
                io_write_bytes=0
            
            nbre_threads=p.num_threads()
            nbre_fils=len(p.children(recursive=False))
            evenement=evenement_processus(timestamp,type,nom,cmdline,pid,duree_execution,cpu_pourcentage,ram_pourcentage,io_read_bytes,io_write_bytes,nbre_threads,nbre_fils)
            log_event(evenement)
        except (ps.NoSuchProcess,ps.AccessDenied):
                continue

def collecter_reseau():
    timestamp=int(time.time()*1000)
    type="network"
    connexions=ps.net_connections(kind='inet')
    nbre_connexions=0
    ports=set()
    ips=set()
    bytes_sent=ps.net_io_counters().bytes_sent
    for connexion in connexions:
        if connexion.status=='ESTABLISHED':
            nbre_connexions=nbre_connexions+1
            if connexion.laddr:
                    ports.add(connexion.laddr.port)
            if connexion.raddr:
                ips.add(connexion.raddr.ip)
    unique_ports=list(ports) if ports else []
    unique_ips=list(ips) if ips else []
    evenement=evenement_reseau(timestamp,type,nbre_connexions,unique_ports,unique_ips,bytes_sent)
    log_event(evenement)
    
    
class CollecteurFichier(FileSystemEventHandler):
    def on_modified(self,evenement):
        timestamp=int(time.time()*1000)
        type="file"
        chemin=evenement.src_path 
        action="modify"
        est_dossier=evenement.is_directory 
        evenement=evenement_fichier(timestamp,type,chemin,action,est_dossier)
        log_event(evenement)
    def on_created(self,evenement):
        timestamp=int(time.time()*1000)
        type="file"
        chemin=evenement.src_path 
        action="create"
        est_dossier=evenement.is_directory 
        evenement=evenement_fichier(timestamp,type,chemin,action,est_dossier)
        log_event(evenement)
    def on_deleted(self,evenement):
        timestamp=int(time.time()*1000)
        type="file"
        chemin=evenement.src_path 
        action="delete"
        est_dossier=evenement.is_directory 
        evenement=evenement_fichier(timestamp,type,chemin,action,est_dossier)
        log_event(evenement)
      
def main():
    observateur=Observer()
    observateur.schedule(CollecteurFichier(),path="/tmp",recursive=True)
    observateur.start()
    try:
        while True:
            collecter_systeme()
            collecter_processus()
            collecter_reseau()
            time.sleep(2)
    except KeyboardInterrupt:
        observateur.stop()

    observateur.join()
    fichier.close()

if __name__ == "__main__":
    main()
