"""
Takes a database of papers in json format, processes them with util/paperStats/paperStats.py and outputs a CSV with the statistics of each paper.

It is expected that the paper files have been downloaded with util/downloadPapers/downloadPapers.py.
PDFs should be in util/downloadPapers/PDF and zipped LaTeX projets in util/downloadPapers/LaTeX.
Their filesnames should be {title}.pdf and {title}.tar.gz respectively.

Sample database entry :

{
    "corpusid": 253523007,
    "externalids": {

        "ArXiv": "2211.08422",
        ...
    },
    "url": "https://www.semanticscholar.org/paper/6472bda2c0c5b72d5ba563e4b0d5bba0c91eccca",
    "title": "Mechanistic Mode Connectivity",
    ...
    "venue": "International Conference on Machine Learning",
    ...
    "year": 2022,
    "referencecount": 127,
    "citationcount": 22,
    "influentialcitationcount": 0,
    ...
}

"""

from multiprocessing import Manager
from tqdm import tqdm
from util.paperStats import paperStats
import colorama
import concurrent.futures
import csv
import json
import os
import re
import tarfile
import tempfile

database = "util/downloadPapers/filtered_database_2020_2021_2022.json"
output = "STATS.csv"

# Methode utilisée par downloadPapers pour nettoyer les noms de fichiers. On l'utilise ici pour retrouver les fichiers à traiter.
def clean_filename(filename):
    # Supprimer les caractères non valides pour un nom de fichier sur Windows
    return re.sub(r'[\\/:"*?<>|]', "", filename)

# Retrouve les données d'un papier dans la base de données à partir de son titre
def getSemanticScholarData(title):

    # Each line is a json object
    lines = []

    with open(database, "r") as f:
        lines += f.readlines()

    # Look for paper with title 'title' in the database
    for line in lines:
        entry = json.loads(line)
        cleaned_entry = clean_filename(entry["title"])
        if cleaned_entry == title:
            break
    else:
        raise ValueError(f"Paper not found in database : {title}")
    

    return {
        "corpusid": entry["corpusid"],
        "arxiv_id": entry["externalids"]["ArXiv"],
        "title": entry["title"],
        "year": entry["year"],
        "venue": entry["venue"],
        "citationcount": entry["citationcount"],
        "referencecount": entry["referencecount"],
        "influentialcitationcount": entry["influentialcitationcount"],
    }


# Parallelize the get_stats function, using k threads
def get_all_stats(k=20):

    titles = []

    nb_final_lines = 0

    pdfLocation = "util/downloadPapers/PDF/"

    # Fill 'lines' with the names of the PDF files located in pdfLocation
    for file in os.listdir(pdfLocation):
        if file.endswith(".pdf"):
            titles.append(file.replace(".pdf", ""))

    titles.sort()

    # Split the lines into k parts for parallel processing
    lines_parts = [
        titles[i::k] for i in range(k)
    ]

    # Process each part in parallel with k threads
    # Each thread will call get_stats with a different part of the lines

    manager = Manager()
    all_stats_by_thread = manager.dict()

    with concurrent.futures.ThreadPoolExecutor(max_workers=k) as executor:
        futures = [executor.submit(get_stats, lines, i) for i, lines in enumerate(lines_parts)]

        # Wait for all threads to finish
        concurrent.futures.wait(futures)

        # Get the results from all threads
        for i, future in enumerate(futures):
            all_stats_by_thread[i] = future.result()
    
    # Merge the results from all threads
    all_stats = {}
    for thread_stats in all_stats_by_thread.values():
        for stats in thread_stats.values():
            all_stats[stats["corpusid"]] = stats

    return all_stats


def get_stats(titles, process_id=0):

    total_lines = len(titles) - 1

    result = {}

    # Itération sur chaque ligne du fichier JSON
    for index, title in tqdm(enumerate(titles,start=0),
        total=total_lines,
        desc=f"T{process_id}"
    ):
        try:

            pdf_path = f"util/downloadPapers/PDF/{title}.pdf"
            latex_path = (
                f"util/downloadPapers/LaTeX/{title}.tar.gz"
            )

            # Unzip the LaTeX project to a temporary directory
            with tempfile.TemporaryDirectory() as tempdir:
                try:
                    with tarfile.open(latex_path, "r:gz") as tar:
                        tar.extractall(tempdir)

                    paper_stats = paperStats.paperStats(pdf_path, tempdir)

                except FileNotFoundError as e:
                    print(
                        f"{colorama.Fore.YELLOW}Fichier non trouvé : {title}{colorama.Style.RESET_ALL}"
                    )
                    raise e
                    continue

                except tarfile.ReadError:
                    print(
                        f"{colorama.Fore.RED}Erreur de décompression GZIP : {title}{colorama.Style.RESET_ALL}"
                    )
                    continue

                except UnicodeDecodeError:
                    print(
                        f"{colorama.Fore.RED}Erreur de décodage Unicode : {title}{colorama.Style.RESET_ALL}"
                    )
                    continue

            filtered_semantic_scholar_data = getSemanticScholarData(title)
            both_stats = filtered_semantic_scholar_data | paper_stats

            result[index] = both_stats

        except Exception as e:
            print(f"Erreur {title} : {e}")
            continue

    return result


def write_csv(stats):
    """
    Stats is a dictionary of dictionaries. Each dictionary is a paper's stats.
    keys are indexes of the paper in the database.
    values are dictionaries of the paper's stats.
    """

    print(f"Writing to {output} with {len(stats)} lines.")

    with open(output, "w", newline="") as csvfile:
        fieldnames = next(iter(stats.values())).keys()

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for index, paper in stats.items():
            writer.writerow(paper)

if __name__ == "__main__":
    write_csv(get_all_stats())
