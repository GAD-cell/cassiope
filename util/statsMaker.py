"""
Takes a database of papers in json format, processes them with paperStats/paperStats.py and outputs a CSV with the statistics of each paper.

It is expected that the paper files have been downloaded with downloadPapers/downloadPapers.py.
PDFs should be in downloadPapers/PDF and zipped LaTeX projets in downloadPapers/LaTeX.
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
from paperStats import paperStats
import colorama
import concurrent.futures
import csv
import json
import os
import re
import tarfile
import tempfile

databases_path = "downloadPapers"
databases = [
    "database_ICML_2018-2022.json"
]
output = "paperStats/STATS_2018-2022.csv"

papers = {}


# Methode utilisée par downloadPapers pour nettoyer les noms de fichiers. On l'utilise ici pour retrouver les fichiers à traiter.
def clean_filename(filename):
    # Fonction pour nettoyer les noms de fichiers
    return "".join(c for c in filename if c.isalnum() or c in (' ', '_', '-')).rstrip()


def prepare_papers():
    # Fill papers with a dict like {cleaned_title: {paper data}}
    for database in databases:
        with open(os.path.join(databases_path, database), "r") as f:
            for line in f:
                entry = json.loads(line)
                cleaned_entry = clean_filename(entry["title"])
                papers[cleaned_entry] = entry

# Retrouve les données d'un papier dans la base de données à partir de son titre
def getSemanticScholarData(title):

    entry = papers.get(clean_filename(title))

    if entry is None:
        print(f"{colorama.Fore.RED}Papier non trouvé dans `papers` : {title}{colorama.Style.RESET_ALL}")
        return {}

    return {
        "corpusid": entry["corpusid"],
        "arxiv_id": entry["externalids"]["ArXiv"],
        "title": entry["title"],
        "authors": entry["authors"],
        "filename": clean_filename(entry["title"]),
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

    pdfLocation = "downloadPapers/PDF/"

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

            pdf_path = f"downloadPapers/PDF/{title}.pdf"
            latex_path = (
                f"downloadPapers/LaTeX/{title}.tar.gz"
            )

            filtered_semantic_scholar_data = getSemanticScholarData(title)
            if not filtered_semantic_scholar_data:
                continue

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
    prepare_papers()
    write_csv(get_all_stats())
