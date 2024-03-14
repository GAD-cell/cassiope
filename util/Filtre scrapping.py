# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 16:17:08 2024

@author: Axel
"""

import json
import csv
import os
import requests

# Créer un dossier pour stocker les papiers téléchargés
dossier_papiers = 'papers'
if not os.path.exists(dossier_papiers):
    os.makedirs(dossier_papiers)

# Compteur pour le nombre de papiers téléchargés
nombre_papiers_telecharges = 0

# Compteur pour le nombre total de lignes filtrées
nombre_lignes_filtrees = 0

# Ouvrir le fichier CSV en mode écriture
with open('donnees.csv', 'w', newline='', encoding='utf-8') as fichier_csv:
    # Définir les noms de colonnes pour le fichier CSV
    colonnes = ['Title', 'Venue', 'Year', 'Authors', 'Category', 'ArXiv', 'Download_Link', 'Paper_Link']
    
    # Créer un objet writer CSV
    writer = csv.DictWriter(fichier_csv, fieldnames=colonnes)
    
    # Écrire les en-têtes de colonnes dans le fichier CSV
    writer.writeheader()

    # Ouvrir le fichier JSON en mode lecture avec l'encodage UTF-8
    with open('20240301.json', 'r', encoding='utf-8') as fichier_json:
        # Parcourir chaque ligne du fichier JSON
        for ligne in fichier_json:

            # Charger la ligne JSON
            donnees = json.loads(ligne)

            # Vérifier les conditions de filtrage : "ArXiv" non "null", "year" qui vaut "2023",
            # "venue" qui vaut "International Conference on Machine Learning"
            if (donnees.get('externalids', {}).get('ArXiv') != 'null' and
                donnees.get('year') == 2023 and
                donnees.get('venue') == 'International Conference on Machine Learning'):
                
                # Incrémenter le compteur de lignes filtrées
                nombre_lignes_filtrees += 1
                
                # Récupérer les valeurs des champs spécifiés
                titre = donnees.get('title', '')
                lieu = donnees.get('venue', '')
                annee = donnees.get('year', '')
                
                # Récupérer les noms des auteurs
                auteurs = ", ".join([auteur.get('name', '') for auteur in donnees.get('authors', [])])
                
                # Récupérer la catégorie, si elle est présente
                categorie = ", ".join([categorie.get('category', '') for categorie in donnees.get('s2fieldsofstudy', [])])
                
                # Récupérer l'identifiant ArXiv
                arxiv = donnees.get('externalids', {}).get('ArXiv', '')
                
                # Construire l'URL de téléchargement du papier ArXiv
                arxiv_url = f"https://arxiv.org/pdf/{arxiv}.pdf"
                
                # Télécharger le papier
                response = requests.get(arxiv_url)
                
                # Vérifier si le téléchargement a réussi
                if response.status_code == 200:
                    # Enregistrer le papier dans le dossier "papers"
                    chemin_fichier = os.path.join(dossier_papiers, f"{arxiv}.pdf")
                    with open(chemin_fichier, 'wb') as fichier_pdf:
                        fichier_pdf.write(response.content)
                    
                    # Mettre à jour le nombre de papiers téléchargés
                    nombre_papiers_telecharges += 1
                    
                    # Afficher le succès du téléchargement
                    print(f"Le papier '{titre}' ({arxiv}) a été téléchargé avec succès.")
                    
                    # Mettre à jour le lien de téléchargement dans le fichier CSV
                    lien_telechargement = f'=HYPERLINK("{arxiv_url}", "Télécharger")'
                    
                    # Mettre à jour le lien vers le papier téléchargé dans le fichier CSV
                    lien_papier = f'=HYPERLINK("{chemin_fichier}", "Papier PDF")'
                    
                    # Écrire les données dans le fichier CSV
                    writer.writerow({'Title': titre, 'Venue': lieu, 'Year': annee, 'Authors': auteurs, 'Category': categorie, 'ArXiv': arxiv, 'Download_Link': lien_telechargement, 'Paper_Link': lien_papier})
                else:
                    # Afficher l'échec du téléchargement
                    print(f"Échec du téléchargement du papier '{titre}' ({arxiv}).")
                
                print("-----------------------")

# Afficher le nombre total de papiers téléchargés
print(f"Nombre total de papiers téléchargés : {nombre_papiers_telecharges}/{nombre_lignes_filtrees}")
