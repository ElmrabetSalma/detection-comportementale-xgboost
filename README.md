<h1> Détection comportementale de programmes suspects</h1>

Système de détection d'anomalies en temps réel basé sur le comportement du système (fichiers, processus, réseau, ressources) et un modèle <b>XGBoost</b> entraîné sur des données bénignes et malveillantes.

> Projet réalisé dans le cadre de mon cycle d'ingénieur en cybersécurité (ENSA Fès).

<h2> Aperçu</h2>

<p align="center">
  <img width="1237" height="706" alt="image" src="https://github.com/user-attachments/assets/13c581d2-86e2-4f6d-ac68-b4b41bb9c93b" />
  <br>
  <em>Interface du tableau de bord et métriques</em>
</p>

<p align="center">
 <img width="1047" height="331" alt="image" src="https://github.com/user-attachments/assets/4dee7f11-ad03-4305-a84b-c23d816f76fd" />
  <br>
  <em>Système normal (aucune anomalie détectée)</em>
</p>

<p align="center">
  <img width="1237" height="482" alt="image" src="https://github.com/user-attachments/assets/9531d86e-3779-4b4e-b8c6-d0d420342e19" />
  <br>
  <em>Détection d'une attaque en temps réel (Burst Fichiers)</em>
</p>

<p align="center">
  <img width="912" height="552" alt="image" src="https://github.com/user-attachments/assets/ae636b47-a2ce-485c-8717-65721b1e9c81" />

  <br>
  <em>Historique des alertes détectées</em>
</p>

<h2> Objectifs</h2>

<ul>
<li>Collecter en continu la télémétrie système (processus, fichiers, réseau, CPU/RAM)</li>
<li>Agréger les événements sur une fenêtre glissante de <b>10 secondes</b> (21 features)</li>
<li>Classifier chaque fenêtre en "Bénin" ou "Suspect" via XGBoost</li>
<li>Identifier automatiquement le "type d'attaque" (Burst, Ransomware, Keylogger, Scan réseau, Exfiltration, Brute Force)</li>
<li>Afficher les résultats en temps réel dans un dashboard Streamlit</li>
</ul>

<h2> Architecture</h2>

<ul>
<li><b>Collecteurs</b> (psutil + watchdog)</li>
<li><b>Buffer d'événements</b> (fenêtre 10s)</li>
<li><b>Extraction de 21 features</b></li>
<li><b>Modèle XGBoost</b> (Prédiction + probabilité)</li>
<li><b>Identification du type d'attaque</b></li>
<li><b>Dashboard Streamlit</b> (alertes + graphiques)</li>
</ul>

<h2> Technologies</h2>

<ul>
<li><b>Python 3.10+</b></li>
<li><b>psutil</b> : collecte processus / réseau / système</li>
<li><b>watchdog</b> : surveillance des événements fichiers</li>
<li><b>XGBoost / Scikit-learn</b> : entraînement & comparaison (Random Forest, Isolation Forest, One-Class SVM)</li>
<li><b>Streamlit + Plotly</b> : dashboard temps réel</li>
<li><b>Pandas / NumPy</b> : traitement des données</li>
</ul>

<h2> Performances du modèle</h2>

<table>
  <thead>
    <tr>
      <th>Modèle</th>
      <th>Accuracy</th>
      <th>Précision</th>
      <th>Recall</th>
      <th>F1-Score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Isolation Forest</td>
      <td>74.75%</td>
      <td>66.37%</td>
      <td>100%</td>
      <td>79.79%</td>
    </tr>
    <tr>
      <td>One-Class SVM</td>
      <td>74.71%</td>
      <td>66.34%</td>
      <td>100%</td>
      <td>79.77%</td>
    </tr>
    <tr>
      <td>Random Forest</td>
      <td>98.82%</td>
      <td>98.85%</td>
      <td>98.79%</td>
      <td>98.82%</td>
    </tr>
    <tr>
      <td><b>XGBoost</b></td>
      <td><b>99.07%</b></td>
      <td><b>99.31%</b></td>
      <td><b>98.82%</b></td>
      <td><b>99.07%</b></td>
    </tr>
  </tbody>
</table>

<p><i>Le XGBoost a été sélectionné pour son excellente précision (99.31%), limitant ainsi les faux positifs.</i></p>

<h2> Lancer le projet</h2>

<h3>1. Installer les dépendances</h3>
<p><code>pip install -r requirements.txt</code></p>

<h3>2. Lancer le Dashboard de détection en temps réel</h3>
<p><code>streamlit run detection/dashboard.py</code></p>

<h3>3. Simuler une attaque (dans un autre terminal)</h3>
<p>Pour tester la détection, lancez l'un des scripts d'attaque :</p>
<ul>
<li><code>python attacks/ransomware.py</code> (Chiffrement massif)</li>
<li><code>python attacks/burst.py</code> (Création/suppression massive)</li>
<li><code>python attacks/scanner.py</code> (Scan de ports)</li>
<li><code>python attacks/keylogger.py</code> (Lecture répétée)</li>
<li><code>python attacks/data_exfiltration.py</code></li>
<li><code>python attacks/force_brute.py</code></li>
</ul>
<p><i>Le dashboard doit lever une alerte (rouge) avec le type d'attaque détecté.</i></p>

<h2> Pipeline de collecte & entraînement (Reproduction)</h2>

<p>Si vous souhaitez reproduire l'entraînement du modèle :</p>

<ol>
<li><b>Collecter du comportement bénin (~10 min)</b> : <br> <code>python collectors/behaviour_collector_benin.py</code></li>
<li><b>Collecter du comportement malveillant (lancer attaques + collector)</b> : <br> <code>python collectors/behaviour_collector_suspect.py</code></li>
<li><b>Extraire les features</b> : <br> <code>python features/extraction_features_benins.py</code> <br> <code>python features/extraction_features_suspects.py</code></li>
<li><b>Préparer le dataset</b> : <br> <code>python ml/preparer_dataset_ml.py</code></li>
<li><b>Comparer les modèles</b> : <br> <code>python ml/entrainer_modeles.py</code></li>
<li><b>Sauvegarder le meilleur modèle</b> : <br> <code>python ml/sauvegarder_meilleur_modele.py</code></li>
</ol>

<h2> Les 21 features extraites</h2>

<ul>
<li><b>Fichiers</b> : nb événements, créés, supprimés, modifiés, fichiers/seconde</li>
<li><b>Processus</b> : nb événements, CPU max/moy, stabilité, threads, octets lus/écrits, ratio I/O</li>
<li><b>Réseau</b> : nb événements, connexions simultanées, ports/IPs distincts, octets envoyés, persistance de port</li>
<li><b>Système</b> : nb événements, total d'événements</li>
</ul>

<h2> Avertissement</h2>

Ce projet est <b>strictement éducatif</b>. Les scripts d'attaque (<code>attacks/</code>) sont conçus pour cibler <code>/tmp</code> sur une machine isolée de test. <b>Ne jamais exécuter sur un système de production ou sur une machine tierce.</b>

<h2> Auteure</h2>

<b>Salma Elmarabet</b> — Élève ingénieure en cybersécurité (ENSA Fès) <br>
<a href="https://www.linkedin.com/in/salma-elmarabet-5a8921323/">LinkedIn</a>
