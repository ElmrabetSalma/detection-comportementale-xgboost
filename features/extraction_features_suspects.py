"""
Extraction des features pour le comportement suspect (attaques).
Lit le fichier de collecte (collecte_resultats_suspects.jsonl), 
calcule les 21 features sur une fenêtre glissante de 10 secondes 
et sauvegarde le résultat dans features_suspects.csv.
"""
import pandas as pd
df=pd.read_json("collecte_resultats_suspects.jsonl", lines=True)    
df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
df=df.set_index("timestamp")
df=df.sort_index()
features_de_frequence = [
    (df["type"]=="file").astype(int),
    ((df["type"]=="file") & (df["action"]=="create")).astype(int),
    ((df["type"]=="file") & (df["action"]=="delete")).astype(int),
    ((df["type"]== "file") & (df["action"] == "modify")).astype(int),
    (df["type"]== "process").astype(int),
    (df["type"]== "network").astype(int),
    (df["type"]== "system").astype(int),
    pd.Series(1, index=df.index)   # total événements
]

df["nombre_d_evenements_file"]=features_de_frequence[0].rolling("10s").sum()
df["nombre_fichiers_crees"]=features_de_frequence[1].rolling("10s").sum()
df["nombre_fichiers_supprimes"]=features_de_frequence[2].rolling("10s").sum()
df["nombre_fichiers_modifies"]=features_de_frequence[3].rolling("10s").sum()
df["nombre_d_evenements_process"]=features_de_frequence[4].rolling("10s").sum()
df["nombre_d_evenements_network"]=features_de_frequence[5].rolling("10s").sum()
df["nombre_d_evenements_system"]=features_de_frequence[6].rolling("10s").sum()
df["nombre_total_d_evenements"]=features_de_frequence[7].rolling("10s").sum()
#reseau
df_reseau= df[df["type"]=="network"].copy()  
df["max_connexions_simultanees"]= df_reseau["nbre_connexions"].rolling("10s").max().reindex(df.index).fillna(0) # Force la Series à avoir exactement le même index (timestamps) que df
df["nombre_ports_distincts"]=df_reseau["unique_ports"].apply( lambda x: len(x) if isinstance(x, list) else 0 ).rolling("10s").sum().reindex(df.index).fillna(0)
df["nombre_ip_distinctes"]=df_reseau["unique_ips"].apply( lambda x: len(x) if isinstance(x, list) else 0 ).rolling("10s").sum().reindex(df.index).fillna(0)
df["octets_envoyes"]=df_reseau["bytes_sent"].diff().rolling("10s").sum().reindex(df.index).fillna(0)  #calcule la différence entre chaque ligne et la précédente
df["port_persistence"] = df_reseau["unique_ports"].apply( lambda x: max([x.count(p) for p in set(x)]) if isinstance(x, list) and x else 0 ).rolling("10s").max().reindex(df.index).fillna(0)
#processus
df_processus= df[df["type"]=="process"].copy()  
df["max_cpu"]=df_processus["cpu_pourcentage"].rolling("10s").max().reindex(df.index).fillna(0)
df["moyenne_cpu"]=df_processus["cpu_pourcentage"].rolling("10s").mean().reindex(df.index).fillna(0)
df["stabilite_cpu"] = df_processus["cpu_pourcentage"].rolling("10s").std().reindex(df.index).fillna(0)
df["max_threads"]=df_processus["nbre_threads"].rolling("10s").max().reindex(df.index).fillna(0)
df["octets_lus"]=df_processus["io_read_bytes"].rolling("10s").sum().reindex(df.index).fillna(0)
df["octets_ecrits"]=df_processus["io_write_bytes"].rolling("10s").sum().reindex(df.index).fillna(0)
# Keylogger: rapport > 5 (lit plus qu'écrit) # Ransomware: rapport ≈ 1 (équilibré)
df["rapport_io"] = (df["octets_lus"] + 1) / (df["octets_ecrits"] + 1)

#feature pour burst
df["fichier_par_seconde"] = df["nombre_fichiers_crees"]/10.0 

#liste des features
features_liste = ["nombre_d_evenements_file", "nombre_fichiers_crees", "nombre_fichiers_supprimes", "nombre_fichiers_modifies", "nombre_d_evenements_process", "nombre_d_evenements_network", "nombre_d_evenements_system", "nombre_total_d_evenements", "max_connexions_simultanees", "nombre_ports_distincts", "nombre_ip_distinctes", "octets_envoyes", "port_persistence", "max_cpu", "moyenne_cpu", "stabilite_cpu", "max_threads", "octets_lus", "octets_ecrits", "rapport_io", "fichier_par_seconde" ]
#Sauvegarder 
df[features_liste].to_csv("features_suspects.csv")


