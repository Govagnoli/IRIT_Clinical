from django.shortcuts import render
from pymongo import MongoClient
import os
from django.conf import settings
import subprocess
import pandas as pd
import pymongo
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def my_view(request):
    if request.method == 'POST':
        file = request.FILES['csv_file']
        filepath = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    context = {'message': 'Fichier enregistré avec succès!'}
    return render(request, 'my_template.html', context)

def execute_exe(request):
    if request.method == 'POST':
        subprocess.run(".\\dist\\majBD.exe", shell=True)
    return render(request, 'execute_exe.html')

def import_exec(request):
    if request.method == 'POST' and 'import' in request.POST:
        file = request.FILES['csv_file']
        filepath = os.path.join(settings.MEDIA_ROOT, file.name)
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        context = {'message': 'Fichier enregistré avec succès!'}
        return render(request, 'Import&Exec.html', context)
    elif request.method == 'POST' and 'execute' in request.POST:
        subprocess.run(".\\dist\\majBD.exe", shell=True)
        context = {'message': 'Fichier exécuté avec succès!'}
        return render(request, 'Import&Exec.html', context)
    else:
        context = {'message': 'erreur'}
    return render(request, 'Import&Exec.html', context)

def requestPNG(request):
    context = {'image_url': "./plot/Essais_rand.png"}
    return render(request, 'test_mongoDb.html', context)
    
def test_mongodb(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["S4"]
    collection_names = ["Essais_rand", "Essais_obs"]
    plot_phases(db.name, collection_names)
    return render(request, 'test_mongoDb.html')

def plot_phases(db_name, collection_names):
    # Connexion à la base de données MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["S4"]
    
    # Initialisation des variables
    phases = ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']
    
    # Récupération des données des collections et comptage des phases
    for collection_name in collection_names:
        counts = []
        collection = db[collection_name]
        for phase in phases:
            count = collection.count_documents({'phase': phase})
            counts.append(count)
    
        # Création du graphique en barres
        x_pos = [i for i, _ in enumerate(phases)]
        plt.bar(x_pos, counts, color='green')
        plt.xlabel("Phases")
        plt.ylabel("Nombre d'essais")
        plt.title(f"Nombre d'essais en phase 1, 2, 3 et 4 pour {collection_name}")
        plt.xticks(x_pos, phases)
    
        # Ajout du nombre de count sur chaque barre
        for i, count in enumerate(counts):
            plt.text(x=i, y=count, s=str(count), ha='center', va='bottom')
        
        # Vérification de l'existence du répertoire "plot"
        if not os.path.exists('plot'):
            os.makedirs('plot')
    
        # Enregistrement du graphique en tant que fichier PNG
        plot_path = os.path.join(settings.PLOT_ROOT, f'{collection_name}.png')
        plt.savefig(plot_path)

        # Fermeture de la figure
        plt.close()


def recupIvermectin(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["S4"]
    collections = [db["Essais_obs"], db["Essais_rand"], db["Pub_obs"], db["Pub_rand"]]
    req = { "title": { "$regex": "Ivermectin", "$options": "i" } }
    df_concat = pd.DataFrame()
    for collection in collections:
        df = pd.DataFrame(list(collection.find(
            req,{
                "_id": 0,
                "id": 1,
                "title": 1,
                "linkout":1
            })))
        df_concat = pd.concat([df_concat, df])
        df_concat = df_concat.reset_index(drop=True)
    client.close()
    return render(request, 'test_mongoDb_Eliott.html', {'df_concat': df_concat})

def plot_genres(db_name, collection_names):
    # Connexion à la base de données MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["S4"]
    # Initialisation des variables
    genders = ['All', 'Female', 'Male']
    counts = {gender: 0 for gender in genders}
    
    # Récupération des données des collections et comptage des phases
    for collection_name in collection_names:
        collection = db[collection_name]
        for gender in genders:
            count = collection.count_documents({'gender': gender})
            counts[gender] += count
            
    
        # Création du graphique en barres
        x_pos = [i for i, _ in enumerate(genders)]
        plt.bar(x_pos, [counts[gender] for gender in genders], color='blue')
        plt.xlabel("Genres")
        plt.ylabel("Nombre d'essais")
        plt.title(f"Nombre d'essais par genre (All, Female, Male)")
        plt.xticks(x_pos, genders)
    
        # Ajout du nombre de count sur chaque barre
        for i, count in enumerate(counts.values()):
            plt.text(x=i, y=count, s=str(count), ha='center', va='bottom')
        
        # Vérification de l'existence du répertoire "plot"
        if not os.path.exists('plot'):
            os.makedirs('plot')
    
        # Enregistrement du graphique en tant que fichier PNG
        plot_path = os.path.join(settings.PLOT_ROOT, 'essais_genres.png')
        plt.savefig(plot_path)

        # Fermeture de la figure
        plt.close()

def def_param_Genres(request):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["S4"]
    collection_names = ["Essais_rand", "Essais_obs"]
    plot_genres(db.name, collection_names)