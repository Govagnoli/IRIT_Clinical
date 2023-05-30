from django.shortcuts import render
from pymongo import MongoClient
import pymongo
import os
from django.conf import settings
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go

CONNEXION_BDD = ""

# Create your views here.
def import_exec(request):
    if request.method == 'POST' and 'import' in request.POST:
        file = request.FILES.get('xlsx_file')
        if file is not None and file.name == '20200601_IRIT_clinicalTrialspublications.xlsx':
            filepath = os.path.join(settings.MEDIA_ROOT, 'Excell', file.name)
            with open(filepath, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            context = {'message': 'Le fichier Excel a été importé avec succès!'}
        else:
            context = {'message': 'Le fichier importé n\'est pas le fichier Excel \'20200601_IRIT_clinicalTrialspublications.xlsx\''}
        return render(request, 'chartapp/Import&Exec.html', context)
    elif request.method == 'POST' and 'execute' in request.POST:
        os.startfile(r'.\\dist\\majBD.exe')
        context = {'message': 'Fichier exécuté avec succès!'}
        return render(request, 'chartapp/Import&Exec.html', context)
    else:
        context = {'message': 'erreur'}
        return render(request, 'chartapp/Import&Exec.html', context)

def plot_phases(request):
    selected_collection = request.GET.get('collection', 'Essais_rand')
    collection_names = ["Essais_rand", "Essais_obs"]
    client = MongoClient(CONNEXION_BDD)
    db = client["S4"]
    
    phases = ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4']
    
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.1)
    
    for i, collection_name in enumerate(collection_names):
        counts = []
        collection = db[collection_name]
        for phase in phases:
            count = collection.count_documents({'phase': phase})
            counts.append(count)

        fig.add_trace(go.Bar(
            x=phases,
            y=counts,
            marker_color='blue',
            name=f'{collection_name}'),
            row=1,
            col=i+1)

        for j, count in enumerate(counts):
            fig.add_annotation(
                x=phases[j],
                y=count,
                text=str(count),
                showarrow=False,
                font=dict(color='black', size=12),
                align='center',
                yshift=10,
                row=1,
                col=i+1)

    fig.update_layout(
        title=f"Nombre d'essais en phase 1, 2, 3 et 4 pour {', '.join(collection_names)}",
        xaxis_title='Phases',
        yaxis_title="Nombre d'essais",
        height=500,
        width=1000,
        showlegend=True,
        legend=dict(
            title='Collections',
            x=1.05,
            y=1,
            traceorder='normal',
            font=dict(
                family='sans-serif',
                size=12,
                color='black'
            ),
            bgcolor='LightSteelBlue',
            bordercolor='Black',
            borderwidth=2
        )
    )
    
    client.close()
    
    graph = fig.to_html(full_html=False, default_height=500, default_width=1000)
    
    return render(request, 'chartapp/plot_phases.html', {'graph': graph, 'collection_names': collection_names, 'selected_collection': selected_collection})

def plot_genres(request):
    selected_collection = request.GET.get('collection', 'Essais_rand')
    collection_names = ["Essais_rand", "Essais_obs"]
    client = MongoClient(CONNEXION_BDD)
    db = client["S4"]
    
    genders = ['All', 'Female', 'Male']
    colors = ['grey','green','yellow']
    
    fig = make_subplots(rows=1, cols=1, shared_yaxes=True, horizontal_spacing=0.1)
    
    for i, collection_name in enumerate(collection_names):
        counts = []
        collection = db[collection_name]
        for gender in genders:
            count = collection.count_documents({'gender': gender})
            counts.append(count)

        fig.add_trace(go.Bar(
            x=genders,
            y=counts,
            marker_color=colors,
            name=f'{collection_name}'))

        for j, count in enumerate(counts):
            fig.add_annotation(
                x=genders[j],
                y=count,
                text=str(count),
                showarrow=False,
                font=dict(color='black', size=12),
                align='center',
                yshift=10,
                row=1,
                col=1)

    fig.update_layout(
        title=f"Nombre d'essais par genre {', '.join(collection_names)}",
        xaxis_title='Genres',
        yaxis_title="Nombre d'essais",
        height=500,
        width=1000,
        showlegend=True,
        legend=dict(
            title='Collections',
            x=1.05,
            y=1,
            traceorder='normal',
            font=dict(
                family='sans-serif',
                size=12,
                color='black'
            ),
            bgcolor='LightSteelBlue',
            bordercolor='Black',
            borderwidth=2
        )
    )
    
    client.close()
    
    graph = fig.to_html(full_html=False, default_height=500, default_width=1000)
    
    return render(request, 'chartapp/plot_phases.html', {'graph': graph, 'collection_names': collection_names, 'selected_collection': selected_collection})

def recupIvermectin(request):
    client = MongoClient(CONNEXION_BDD)
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
    return render(request, 'chartApp/Ivermectin.html', {'df_concat': df_concat.to_html})

#Publications du mois courant (ex mai 2020) triées par score altmetric décroissant et départagées par citations décroissantes
def PubliPlusAbstract(request):
    client = MongoClient(CONNEXION_BDD)
    db = client["S4"]
    collections = [db["Pub_obs"], db["Pub_rand"]]
    df_concat = pd.DataFrame()
    # Requête MongoDB pour récupérer les documents pertinents
    for collection in collections:
        result = pd.DataFrame(
            list(
                db["Pub_obs"].aggregate([
                    {
                        "$project": {
                            "id": 1,
                            "linkout": 1,
                            "year": {"$year": {"date": {"$dateFromString": {"dateString": "$datePublished"}}}},
                            "month": {"$month": {"date": {"$dateFromString": {"dateString": "$datePublished"}}}},
                            "altmetric": 1,
                            "timesCited": 1
                        }
                    },
                    {
                        "$group": {
                            "_id": {"year": "$year", "month": "$month"},
                            "maxAltmetric": {"$max": "$altmetric"},
                            "maxCitation": {"$max": "$timesCited"},
                            "id": {"$first": "$id"},
                            "linkout": {"$first": "$linkout"}
                        }
                    },
                    {
                        "$sort": {"_id.year": -1, "_id.month": -1}
                    }
                ])
            )
        )
        df_concat = pd.concat([df_concat, result])
    df_concat = df_concat.reset_index(drop=True)
    df_concat = df_concat[df_concat["linkout"].notnull()]
    df_concat = df_concat[['id', 'linkout', 'maxAltmetric']]
    client.close()
    return render(request, 'chartapp/publications_du_mois.html', {'data': df_concat.to_html()})

def ExtraireConcepts(request):
    try:
        client = MongoClient(CONNEXION_BDD)
        db = client["S4"]
        collection = db["vueConcept"] 
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to server: %s" % e)
       
    dfConcepts = pd.DataFrame()
    df = pd.DataFrame()
    try:
        dfConcepts = pd.DataFrame(list(
            collection.aggregate([
                { '$unwind': '$Concepts' },
                { '$unwind': '$Concepts' },
                { '$group': { '_id': '$Concepts', 'count': { '$sum': 1 } } },
                { '$sort': {"count": -1}},
                { '$limit': 10 }
            ])
        ))
        client.close()
    except pymongo.errors as e:
        print("Erreur lors de la récupération des données : %s" % e)
        client.close()

    dfConcepts = dfConcepts.reset_index(drop=True)
    
    return render(request, 'chartApp/Concepts-frequents.html', {'dfConcepts': dfConcepts.to_html()})

def LabelDrugs(request):
    client = MongoClient(CONNEXION_BDD)
    db = client["S4"]
    collections = [db["Essais_obs"], db["Essais_rand"]]
    req = {"interventions": { "$regex": "Drug", "$options": "i" }}
    df_concat = pd.DataFrame()
    for collection in collections:
        df = pd.DataFrame(list(collection.find(
            req,{
                "_id": 0,
                "id": 1,
                "title": 1,
                "linkout":1,
                "date": 1
            })))
        df_concat = pd.concat([df_concat, df])
    df_concat = df_concat.sort_values('date')
    df_concat = df_concat.reset_index(drop=True)
    client.close()
    return render(request, 'chartApp/Interventions_drugs.html', {'df_concat': df_concat.to_html})

def corpus(request, columns=None):
    client = MongoClient(CONNEXION_BDD)
    db = client["S4"]

    collection_rand = db['Essais_rand']
    corpus_data_rand = list(collection_rand.find())
    df_rand = pd.DataFrame(corpus_data_rand)

    collection_obs = db['Essais_obs']
    corpus_data_obs = list(collection_obs.find())
    df_obs = pd.DataFrame(corpus_data_obs)

    df = pd.concat([df_rand, df_obs], ignore_index=True)

    if columns is not None:
        df = df[columns]
    else:
        df = df[['id', 'title', 'registry', 'linkout', 'phase']]

    search_query = request.GET.get('search')
    if search_query:
        df = df[df['id'].str.contains(search_query)]

    selected_phase = request.GET.get('phase')
    if selected_phase != 'All':
        df = df.loc[df['phase'] == selected_phase]

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df[col] for col in df.columns],
                   fill_color='lavender',
                   align='left'))
    ])

    fig.update_layout(title='Corpus des Essais',
                      height=800,
                      width=1900, )
    fig = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[df[col] for col in df.columns],
            fill_color='lavender',
            align='left'))
    ])

    fig.update_layout(title='Corpus des Essais')

    fig.add_trace(go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.sort_values(by=['title'])[col] for col in df.columns],
                fill_color='lavender',
                align='left'))
    )

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                buttons=[
                    dict(
                        args=[{"visible": [True, False]}],
                        label="Trier par ID",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, True]}],
                        label="Trier par titre",
                        method="update"
                    )
                ]
            )
        ]
    )

    context = {'graph': fig.to_html(full_html=False)}
    return render(request, 'chartapp/corpus.html', context)
