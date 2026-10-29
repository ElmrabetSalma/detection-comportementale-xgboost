"""
Préparation du dataset pour l'apprentissage automatique.
Fusionne les données bénignes et suspectes, mélange le dataset,
sépare les features (X) des labels (Y), effectue un split train/test (80/20)
et sauvegarde les fichiers CSV (X_train, X_test, Y_train, Y_test).
"""
import pandas as pd
from sklearn.model_selection import train_test_split
benins=pd.read_csv("features_benins.csv",index_col=0) 
suspects=pd.read_csv("features_suspects.csv",index_col=0)
benins['label']=0 
suspects['label']=1
# Fusionner
df=pd.concat([benins, suspects],ignore_index=True)
# Mélanger 
df=df.sample(frac=1,random_state=42).reset_index(drop=True)
# Séparer X (features) et y (labels) 
X=df.drop('label',axis=1)    #entrees
Y=df['label']                            #resultat
# Split train/test (80/20 stratifié) 
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.2,random_state=42,stratify=Y)
#  Sauvegarder
X_train.to_csv("X_train.csv",index=False) 
X_test.to_csv("X_test.csv",index=False) 
Y_train.to_csv("Y_train.csv",index=False,header=['label']) 
Y_test.to_csv("Y_test.csv",index=False,header=['label'])


