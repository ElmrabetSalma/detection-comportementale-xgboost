"""
Entraînement et comparaison des modèles.
Charge les données d'entraînement et de test (X_train, X_test, Y_train, Y_test),
entraîne 4 modèles (Isolation Forest, One-Class SVM, Random Forest, XGBoost),
les évalue (accuracy, précision, recall, F1) et sauvegarde le tableau 
comparatif dans comparaison_modeles.csv.
"""
import pandas as pd  
import numpy as np  
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
#charger les données
X_train=pd.read_csv("X_train.csv")
X_test=pd.read_csv("X_test.csv")
Y_train=pd.read_csv("Y_train.csv").values.ravel()  #parce que sklearn ne travaille pas sur des dataframes
Y_test=pd.read_csv("Y_test.csv").values.ravel()

#donnees de test: benin
X_train_benin=X_train[Y_train==0]

#modele 1: Isolation forest pour 
modele1=IsolationForest(contamination=0.5,random_state=42,n_jobs=-1)
modele1.fit(X_train_benin)
predictions1=modele1.predict(X_test)   #un tableau NumPy, pas une liste Python
predictions1=np.where(predictions1==1,0,1) #(prediction=1 => 0 sinon =>1), parce qu'on a que labels 0 et 1



#modele 2: One-Class SVM 
modele2=OneClassSVM(nu=0.5,kernel='rbf',gamma='scale')
modele2.fit(X_train_benin)
predictions2=modele2.predict(X_test)
predictions2=np.where(predictions2==1,0,1)


#modele 3: Random Forest qui s'entraine sur benin et suspect 
modele3=RandomForestClassifier(n_estimators=100,random_state=42,n_jobs=-1)
modele3.fit(X_train,Y_train)
predictions3=modele3.predict(X_test)

#modele 4: Xgboost qui s'entraine sur benin et suspect
modele4=XGBClassifier(n_estimators=100,random_state=42,eval_metric='logloss',n_jobs=-1)
modele4.fit(X_train,Y_train)
predictions4=modele4.predict(X_test)


#Evaluation
def eval_model(nom,y_sur,y_pred):
    return {
        "modele": nom,
        "accuracy":accuracy_score(y_sur,y_pred),          #Nombre de prédictions correctes​/nombre total de predictions
        "precision":precision_score(y_sur,y_pred),   #Parmi ce que je signale comme anomalie, combien sont réellement des anomalies ?
        "recall":recall_score(y_sur,y_pred),         #Parmi les vraies anomalies, combien je detecte ?
        "f1":f1_score(y_sur,y_pred)       #moyenne harmonique de la précision et du rappel(recall)
    }
results=pd.DataFrame([
    eval_model("Isolation Forest",Y_test,predictions1),
    eval_model("One-Class SVM",Y_test,predictions2),
    eval_model("Random Forest",Y_test,predictions3),
    eval_model("XGBoost",Y_test,predictions4)
])
results.to_csv("comparaison_modeles.csv",index=False)





