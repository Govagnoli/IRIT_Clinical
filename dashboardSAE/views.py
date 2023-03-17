from django.shortcuts import render
from pymongo import MongoClient
import os
from django.conf import settings

def my_view(request):
    if request.method == 'POST':
        file = request.FILES['csv_file']
        filepath = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    context = {'message': 'Fichier enregistré avec succès!'}
    return render(request, 'my_template.html', context)

def test_mongodb(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["S4"]
    collection = db["Essais_rand"]
    data = collection.find_one()
    return render(request, 'test_mongoDb.html', {'data': data})

def import_csv(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        file_path = os.path.join(settings.BASE_DIR, 'uploads', myfile.name) # Chemin vers le répertoire de votre choix, ici 'uploads'
        with open(file_path, 'wb+') as destination:
            for chunk in myfile.chunks():
                destination.write(chunk)
        return render(request, 'import_csv.html', {'success': True})
    return render(request, 'import_csv.html')

import pymongo
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk

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

#Retoure les données d'une collection dans un dataFrame pandas
def recupDataBd(collection):
    client = getConnexion()
    #Récupération des données de la base dans des dataframes
    data = list(collection.find())
    return pd.DataFrame(data)

client = getConnexion()
db = client["S4"]
collections = [db["Essais_obs"], db["Essais_rand"], db["Pub_obs"], db["Pub_rand"]]

Essais_obs = recupDataBd(collections[0])
Essais_rand = recupDataBd(collections[1])
Pub_obs = recupDataBd(collections[2])
Pub_rand = recupDataBd(collections[3])

#id, title, linkout
def recupIvermectin(collection):
    req = { "title": { "$regex": "Ivermectin", "$options": "i" } }
    df = pd.DataFrame(list(collection.find(
        req,{
            "_id": 0,
            "id": 1,
            "title": 1,
            "linkout":1
        })))
    return df

df_1 = recupIvermectin(collections[0])
df_2 = recupIvermectin(collections[1])
df_3 = recupIvermectin(collections[2])
df_4 = recupIvermectin(collections[3])

#Enregistre les Identifiant, les titres et les liens ayant parlé de Ivermectin dans leur titre. Ils sont enregistré dans un fichier Excell
df_concat = pd.concat([df_1, df_2, df_3, df_4])
df_concat = df_concat.reset_index(drop=True)
df_concat.to_excel("Dashboard/recupIvermectin.xlsx")


