"""
Entraînement et sauvegarde du modèle final (XGBoost).
Charge les données d'entraînement, entraîne le modèle XGBoost 
et le sauvegarde dans le dossier modele_final/.
Sauvegarde également la liste des features utilisées dans features.json.
"""
from xgboost import XGBClassifier
import joblib
import pandas as pd
import json

#charger les données
X_train=pd.read_csv("X_train.csv")
Y_train=pd.read_csv("Y_train.csv").values.ravel()

#meilleur modele Xgboost 
modele=XGBClassifier(n_estimators=100,random_state=42,eval_metric='logloss',n_jobs=-1)
modele.fit(X_train,Y_train)


#sauvegarder le modele
chemin_modele="modele_final/modele_xgboost.pkl"
joblib.dump(modele,chemin_modele)

#sauvegarder les noms des features 
chemin_features="modele_final/features.json"
with open(chemin_features,'w') as f:
    json.dump(list(X_train.columns),f,indent=2)
    






