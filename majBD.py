import pymongo
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import openpyxl
import csv
import os

#Constantes, correspondant au nom des fichier csv.
ESSAIS_OBS = "CSV/1 - ClinicalTrials_ObsStudies.csv"
ESSAIS_RAND = "CSV/2 - ClinicalTrials_RandTrials.csv"
PUB_OBS = "CSV/3 - Publications_ObsStudies.csv"
PUB_RAND = "CSV/4 - Publications_RandTrials.csv"
fichiers = [ESSAIS_OBS, ESSAIS_RAND, PUB_OBS, PUB_RAND]

estConnectee = False
client = None

#Permet de créer la connexion.
def getConnexion():
    global estConnectee
    global client
    if(estConnectee == False):
        #Création de la connexion avec le serveur local.
        client = pymongo.MongoClient("mongodb://localhost:27017")
        return client
    else:
        return client

#Permet de supprimer un fichier
#fichier est un string correspondant au chemin absolu ou relatif du fichier à supprimer.
def supprFichier(fichier):
    if os.path.isfile(fichier):
        os.remove(fichier)
        print("Le fichier (" + fichier + ") a été supprimé avec succès.")
    else:
        print("Le fichier n'existe pas.")

#Transforme une feuille d'un fichier Excell en CSV
def csv_from_excel(feuille):
    wb = openpyxl.load_workbook('Excell/20200601_IRIT_clinicalTrialspublications.xlsx')
    sh = wb[feuille]
    your_csv_file = open('CSV/'+feuille+'.csv', 'w', newline='', encoding='utf-8')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for row in sh.iter_rows():
        wr.writerow([cell.value for cell in row])

    your_csv_file.close()

#
def majBD():
    #récupère ou créer la connexion à la BD
    client = getConnexion()
    #On récupère notre base de données et on liste toutes ses collections
    db = client["S4"]
    collections = [db["Essais_obs"], db["Essais_rand"], db["Pub_obs"], db["Pub_rand"]]
    #On itère sur chaque collection
    i = 0
    for collection in collections:
        #On récupère les données des fichiers CSV
        data = pd.read_csv(fichiers[i])
        #On retire les données Null
        data = data[data["id"].notnull()]
        data.drop_duplicates(subset=['id'], keep='last', inplace=True)
        #On insère les données dans la base de données Mongo
        data_dict = data.to_dict('records')
        #On supprime les anciennes données
        collection.delete_many({})
        #On insère les nouvelles données
        collection.insert_many(data_dict)
        i += 1
    client.close()

# Créer une fenêtre contextuelle avec les boutons "Oui" et "Annuler"
reponse = messagebox.askyesno("Mise à jour de la base de données", "Voulez-vous mettre à jour la base de données ? Les anciennes données seront écrasées.")

# Si l'utilisateur a cliqué sur le bouton "Oui", ça execute le code correspondant
if reponse:
    # création des fichiers CSV
    csv_from_excel('1 - ClinicalTrials_ObsStudies')
    csv_from_excel('2 - ClinicalTrials_RandTrials') 
    csv_from_excel('3 - Publications_ObsStudies') 
    csv_from_excel('4 - Publications_RandTrials')
    #Mise à jour de la BD
    majBD()
    #suppression des fichiers CSV
    supprFichier('CSV/1 - ClinicalTrials_ObsStudies.csv')
    supprFichier('CSV/2 - ClinicalTrials_RandTrials.csv')
    supprFichier('CSV/3 - Publications_ObsStudies.csv')
    supprFichier('CSV/4 - Publications_RandTrials.csv')
