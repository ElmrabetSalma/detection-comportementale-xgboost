"""
Script de simulation d'attaque par force brute sur un fichier chiffré AES.
Tente de déchiffrer /tmp/secret_data.enc en testant 100 000 mots de passe générés aléatoirement,
puis le mot de passe "salma". Conçu pour être détecté par l'EDR de détection comportementale.
"""
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import time
import string
import secrets

fichier="/tmp/secret_data.enc"
fichier_dechiffre="/tmp/secret_data.txt"

with open(fichier,"rb") as f:
    donnees=f.read()
def decrypt_file(password):
        cle_aes=hashlib.sha256(password.encode()).digest()
        # Chiffrement AES
        cipher = AES.new(cle_aes,AES.MODE_ECB)
        try:
            donnees_dechiffrees=unpad(cipher.decrypt(donnees),AES.block_size)
            if "admin" in donnees_dechiffrees.decode():
                with open(fichier_dechiffre,"wb") as f:
                    f.write(donnees_dechiffrees)
        except (ValueError):
            pass

liste_passwords=[]
for i in range(1,100001):
    liste_passwords.append(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(5)))
liste_passwords.append("salma")
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=50) as executor:
    for password in liste_passwords:
        executor.submit(decrypt_file,password)
        time.sleep(0.0006)
