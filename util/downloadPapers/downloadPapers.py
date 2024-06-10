# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 21:19:31 2024

@author: Axel
"""

import os
import json
import gzip
import requests
from tqdm import tqdm
import re
import fnmatch
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed

#VENUE = "International Conference on Machine Learning"
YEARS = [
    2018,
    2019,
    2020, 
    2021, 
    2022,
]

#venue_initials = "".join([word[0] for word in VENUE.split() if word[0].isupper()]).upper() # "ICML" pour International Conference on Machine Learning, etc...

def getLinks():
    # Define base URL for datasets API
    base_url = "https://api.semanticscholar.org/datasets/v1/release/"

    # This endpoint requires authentication via api key
    api_key = "null"
    headers = {"x-api-key": api_key}

    # Make the initial request to get the list of releases
    response = requests.get(base_url)

    if response.status_code == 200:
        # Assume we want data from the latest release, which will correspond to the last item in the response list since releases are ordered chronologically
        release_id = response.json()[-1]

        # Make a request to get datasets available in the latest release (this endpoint url is the release id appended to the base url)
        datasets_response = requests.get(base_url + release_id)

        if datasets_response.status_code == 200:
            # Fetch the datasets list from the response
            datasets = datasets_response.json()["datasets"]

            # Check if the 'papers' dataset exists
            papers_dataset_exists = any(
                dataset.get("name") == "papers" for dataset in datasets
            )

            if papers_dataset_exists:
                # Make a request to get download links for the 'papers' dataset
                dataset_name = "papers"
                download_links_response = requests.get(
                    base_url + release_id + "/dataset/" + dataset_name, headers=headers
                )

                if download_links_response.status_code == 200:
                    download_links = download_links_response.json()["files"]

                    # Your code to process the download links goes here
                    # Appel de la fonction pour télécharger les fichiers
                    return download_links

                else:
                    return f"Failed to get download links. Status code: {download_links_response.status_code}"
            else:
                return "The 'papers' dataset does not exist in the list."
        else:
            return (
                f"Failed to get datasets. Status code: {datasets_response.status_code}"
            )
    else:
        return f"Failed to get releases. Status code: {response.status_code}"


def telecharger_et_traiter_subsets(liens):

    # Dossier de destination pour sauvegarder les fichiers téléchargés
    dossier_destination = "datasets"

    # Itérer sur chaque lien
    for i, lien in enumerate(liens, start=1):
        print(f"Téléchargement et traitement du subset {i}/{len(liens)}...")
        filtered_database = telecharger_et_traiter_subset(lien, dossier_destination, i)
    return filtered_database


def telecharger_et_traiter_subset(lien, dossier_destination, index):
    # Vérifier si le dossier de destination existe, sinon le créer
    if not os.path.exists(dossier_destination):
        os.makedirs(dossier_destination)

    # Nom du fichier téléchargé
    nom_fichier = f"subset_{index}.gz"
    chemin_fichier = os.path.join(dossier_destination, nom_fichier)

    # Téléchargement du subset
    telecharger_fichier(lien, chemin_fichier)

    # Vérification de l'intégrité du fichier téléchargé
    if verifier_integrite(chemin_fichier):
        print("Téléchargement réussi et fichier intègre.")
        # Traitement du subset
        filtered_database = traiter_subset(chemin_fichier)
    else:
        print("Erreur : Le fichier téléchargé est corrompu.")


def telecharger_fichier(lien, chemin_destination):
    # Téléchargement du fichier avec tqdm pour afficher la progression
    with requests.get(lien, stream=True) as r:
        taille_fichier = int(
            r.headers.get("content-length", 0)
        )  # Taille du fichier à télécharger
        taille_unitaire = 128 * 1024  # Taille unitaire en octets
        bar = tqdm(
            total=taille_fichier,
            unit="B",
            unit_scale=True,
            desc=os.path.basename(chemin_destination),
            ncols=100,
        )
        with open(chemin_destination, "wb") as fichier:
            for morceau in r.iter_content(chunk_size=taille_unitaire):
                fichier.write(morceau)
                bar.update(len(morceau))
        bar.close()


def verifier_integrite(chemin_fichier):
    # Vérifier l'intégrité du fichier en vérifiant sa taille
    return os.path.getsize(chemin_fichier) > 0


def traiter_subset(chemin_archive):
    # Ouvrir le fichier gzip en mode lecture
    with gzip.open(chemin_archive, "rb") as gz_file:
        # Créer une liste pour stocker les lignes filtrées
        lignes_filtrees = []

        # Lire le fichier ligne par ligne
        for ligne in tqdm(gz_file, desc="Traitement du fichier", unit=" ligne"):
            # Charger la ligne JSON
            try:
                ligne_json = json.loads(ligne)
            except json.JSONDecodeError:
                continue  # Ignorer les lignes non valides

            # Vérifier si la ligne satisfait les critères
            if est_valide(ligne_json):
                lignes_filtrees.append(ligne_json)

    # Écrire les lignes filtrées dans un fichier JSON
    #chemin_fichier_filtre = f"database_{venue_initials}_{YEARS[0]}-{YEARS[-1]}.json"
    chemin_fichier_filtre = "database_NEURIPS_2018-2022.json"
    with open(chemin_fichier_filtre, "a") as fichier_filtre:
        for ligne in lignes_filtrees:
            json.dump(ligne, fichier_filtre)
            fichier_filtre.write("\n")

    # Supprimer l'archive une fois le traitement terminé
    os.remove(chemin_archive)
    print("Traitement terminé. L'archive a été supprimée avec succès")
    print(str(len(lignes_filtrees)) + " lignes ont été ajoutées à la base de données")
    return chemin_fichier_filtre


def est_valide(ligne_json):
    # Vérifier si la ligne satisfait les critères
    return (
        ligne_json.get("venue", "").lower().find("neurips") != -1
        and
        ligne_json.get("year", "") in YEARS
    )


def clean_filename(filename):
    # Fonction pour nettoyer les noms de fichiers
    return "".join(c for c in filename if c.isalnum() or c in (' ', '_', '-')).rstrip()

def download_papers_from_json(json_file_path):
    # Création des dossiers s'ils n'existent pas
    pdf_folder_path = "PDF"
    latex_folder_path = "LaTeX"
    os.makedirs(pdf_folder_path, exist_ok=True)
    os.makedirs(latex_folder_path, exist_ok=True)

    # Ouverture du fichier JSON
    with open(json_file_path, "r") as file:
        lines = file.readlines()

        # Compteur de papiers téléchargés
        total_papers = len(lines)
        downloaded_papers = 0

        total_lines = len(lines)

        # Itération sur chaque ligne du fichier JSON
        for index, line in enumerate(lines, start=1):
            try:
                paper_data = json.loads(line)
                arxiv_id = paper_data["externalids"]["ArXiv"]
                year = paper_data["year"]
                paper_title = paper_data["title"]

                print(f"[{index}/{total_lines}] ", end="")

                # Vérifier l'année du papier
                if year not in [2018, 2019]:
                    print(f"Année non conforme (2018 ou 2019 requise) : {paper_title}")
                    total_papers -= 1
                    continue

                # Vérifier si le fichier a déjà été téléchargé
                cleaned_title = clean_filename(paper_title)
                pdf_file_path = os.path.join(pdf_folder_path, f"{cleaned_title}.pdf")
                latex_file_path = os.path.join(latex_folder_path, f"{cleaned_title}.tar.gz")
                if os.path.exists(pdf_file_path) and os.path.exists(latex_file_path):
                    print(f"Le fichier existe déjà : {paper_title}")
                    continue

                if arxiv_id:
                    # Construction des liens de téléchargement
                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                    latex_url = f"https://arxiv.org/e-print/{arxiv_id}"

                    # Téléchargement du PDF
                    pdf_response = requests.get(pdf_url)
                    if pdf_response.status_code == 200:
                        # Nettoyage du nom de fichier
                        cleaned_title = clean_filename(paper_title)
                        pdf_file_path = os.path.join(pdf_folder_path, f"{cleaned_title}.pdf")
                        with open(pdf_file_path, "wb") as pdf_file:
                            pdf_file.write(pdf_response.content)
                        print(f"Téléchargement réussi : {paper_title} (PDF)")
                        downloaded_papers += 1
                    else:
                        print(f"Échec du téléchargement : {paper_title} (PDF)")

                    # Téléchargement du LaTeX
                    # Le projet LaTeX est un fichier zip
                    latex_response = requests.get(latex_url)
                    if latex_response.status_code == 200:
                        # Nettoyage du nom de fichier
                        cleaned_title = clean_filename(paper_title)
                        latex_file_path = os.path.join(latex_folder_path, f"{cleaned_title}.tar.gz")
                        with open(latex_file_path, "wb") as latex_file:
                            latex_file.write(latex_response.content)
                        print(f"Téléchargement réussi : {paper_title} (LaTeX)")
                    else:
                        print(f"Échec du téléchargement : {paper_title} (LaTeX)")
                else:
                    print(f"Pas de lien ArXiv disponible pour : {paper_title}")
                    total_papers -= 1  # Décrémenter le nombre total de papiers à télécharger
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON sur la ligne {index}: {line}")

    # Affichage du nombre total de papiers téléchargés
    print(f"Nombre total de papiers téléchargés : {downloaded_papers} sur {total_papers}")

def format_json_file(input_file):
    output_file = "formatted_output.json"
    with open(input_file, "r") as f:
        lines = f.readlines()

    # Ajoute une virgule à la fin de chaque ligne, sauf la dernière et l'avant-dernière
    for i in range(len(lines) - 1):
        lines[i] = lines[i].strip() + ",\n"

    # Ajoute '[' au début et ']' à la fin
    lines[0] = "[\n" + lines[0].lstrip()
    lines[-1] = lines[-1].rstrip() + "\n]"

    # Écrit le fichier formaté
    with open(output_file, "w") as f:
        f.writelines(lines)

    return output_file


def main():
    # Télecharger les liens de la last_release
    links = getLinks()
    # On télécharge les papiers neurips 2018-2022
    #telecharger_et_traiter_subsets(links)
    # La fonction en dessous créer deux dossiers : "PDF" et "LaTeX", qui vont contenir après téléchargement tout les papiers du .json et qui sont bien référencés sur ArXiv
    download_papers_from_json("database_ICML_2018-2022.json")
    '''
    for file in os.listdir('.'):
        if fnmatch.fnmatch(file, 'database_*.json'):
            download_papers_from_json(file)
    '''
    return


if __name__ == "__main__":
    main()
