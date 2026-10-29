🛡️ Détection comportementale de programmes suspects
Système de détection d'anomalies en temps réel basé sur le comportement du système (fichiers, processus, réseau, ressources) et un modèle XGBoost entraîné sur des données bénignes et malveillantes.

Projet réalisé dans le cadre de mon cycle d'ingénieur en cybersécurité (ENSA Fès).

📸 Aperçu
<p align="center"> <img src="https://github.com/user-attachments/assets/33028848-daeb-4dce-ab4a-4c94dbd08889" width="80%" alt="Dashboard" /> <br> <em>Interface du tableau de bord et métriques</em> </p><p align="center"> <img src="https://github.com/user-attachments/assets/7db7ba38-a564-4f36-b177-93914bd73f42" width="80%" alt="Alerte" /> <br> <em>Détection d'une attaque en temps réel</em> </p>
🎯 Objectifs
Collecter en continu la télémétrie système (processus, fichiers, réseau, CPU/RAM)

Agréger les événements sur une fenêtre glissante de 10 secondes (21 features)

Classifier chaque fenêtre en "Bénin" ou "Suspect" via XGBoost

Identifier automatiquement le "type d'attaque" (Burst, Ransomware, Keylogger, Scan réseau, Exfiltration, Brute Force)

Afficher les résultats en temps réel dans un dashboard Streamlit

🏗️ Architecture
text
Collecteurs (psutil + watchdog)
            ↓
Buffer d'événements (fenêtre 10s)
            ↓
Extraction de 21 features
            ↓
Modèle XGBoost → Prédiction + probabilité
            ↓
Identification du type d'attaque
            ↓
Dashboard Streamlit (alertes + graphiques)
🛠️ Technologies
Python 3.10+

psutil : collecte processus / réseau / système

watchdog : surveillance des événements fichiers

XGBoost / Scikit-learn : entraînement & comparaison (Random Forest, Isolation Forest, One-Class SVM)

Streamlit + Plotly : dashboard temps réel

Pandas / NumPy : traitement des données

📊 Performances du modèle
Modèle	Accuracy	Précision	Recall	F1-Score
Isolation Forest	74.75%	66.37%	100%	79.79%
One-Class SVM	74.71%	66.34%	100%	79.77%
Random Forest	98.82%	98.85%	98.79%	98.82%
XGBoost	99.07%	99.31%	98.82%	99.07%
Le XGBoost a été sélectionné pour son excellente précision (99.31%), limitant ainsi les faux positifs.

🚀 Lancer le projet
1. Installer les dépendances
bash
pip install -r requirements.txt
2. Lancer le Dashboard de détection en temps réel
bash
streamlit run detection/dashboard.py
3. Simuler une attaque (dans un autre terminal)
Pour tester la détection, lancez l'un des scripts d'attaque :

bash
python attacks/ransomware.py       # Chiffrement massif
python attacks/burst.py            # Création/suppression massive
python attacks/scanner.py          # Scan de ports
python attacks/keylogger.py        # Lecture répétée
python attacks/data_exfiltration.py
python attacks/force_brute.py
Le dashboard doit lever une alerte (rouge) avec le type d'attaque détecté.

🔬 Pipeline de collecte & entraînement (Reproduction)
Si vous souhaitez reproduire l'entraînement du modèle :

bash
# 1. Collecter du comportement bénin (~10 min)
python collectors/behaviour_collector_benin.py

# 2. Collecter du comportement malveillant (lancer attaques + collector)
python collectors/behaviour_collector_suspect.py

# 3. Extraire les features
python features/extraction_features_benins.py
python features/extraction_features_suspects.py

# 4. Préparer le dataset
python ml/preparer_dataset_ml.py

# 5. Comparer les modèles
python ml/entrainer_modeles.py

# 6. Sauvegarder le meilleur modèle
python ml/sauvegarder_meilleur_modele.py
🧠 Les 21 features extraites
Fichiers : nb événements, créés, supprimés, modifiés, fichiers/seconde

Processus : nb événements, CPU max/moy, stabilité, threads, octets lus/écrits, ratio I/O

Réseau : nb événements, connexions simultanées, ports/IPs distincts, octets envoyés, persistance de port

Système : nb événements, total d'événements

⚠️ Avertissement
Ce projet est strictement éducatif. Les scripts d'attaque (attacks/) sont conçus pour cibler /tmp sur une machine isolée de test. Ne jamais exécuter sur un système de production ou sur une machine tierce.

👤 Auteure
Salma Elmarabet — Élève ingénieure en cybersécurité (ENSA Fès)
