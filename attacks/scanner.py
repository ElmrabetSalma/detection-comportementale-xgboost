"""
Script de simulation de Scan Réseau (Scan de ports).
Utilise une approche multi-threads pour tester l'ouverture des ports 
de 1 à 600 sur une adresse IP cible (par défaut localhost). 
Génère un grand nombre de connexions pour déclencher la détection.
"""
import socket
from threading import Thread
import sys
import time
def scan_port(ip,port):
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(1)
        result=s.connect_ex((ip,port)) # 0 = ouvert
        if result==0:
            print(f"{ip}:{port}")
            time.sleep(10)
            s.close()
    except:
        pass
ip="127.0.0.1"
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=20) as executor:
    for port in range(1,601):
        executor.submit(scan_port,ip,port)
