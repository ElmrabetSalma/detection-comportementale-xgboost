"""
Script de simulation d'attaque Burst.
Crée 10 000 fichiers temporaires dans /tmp en écrivant des données aléatoires,
puis les supprime tous 2 secondes plus tard. 
Cette attaque sature les entrées/sorties (I/O) et les événements fichiers 
"""
import tempfile as tf
import os
import time
fichiers=[]
for i in range(10000):
    descripteur,chemin=tf.mkstemp(suffix='.tmp',prefix='burst_',dir='/tmp',text=False)
    fichiers.append(chemin)
    os.write(descripteur,os.urandom(100)) 
    os.close(descripteur) 
    
time.sleep(2)
for j in range(10000):
    os.unlink(fichiers[j])
