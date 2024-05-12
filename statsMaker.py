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

import json
import tempfile
import tarfile
from util.paperStats import paperStats
import csv
import colorama

database = "util/downloadPapers/database_filtered.json"
output = "STATS.csv"


def filterDatabaseEntryKeys(entry):
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


def get_stats():

    all_stats = {}

    with open(database, "r") as file:
        lines = file.readlines()

    total_lines = len(lines) - 1

    # Itération sur chaque ligne du fichier JSON
    for index, line in enumerate(lines, start=0):
        try:
            semantic_scholar_data = json.loads(line)
            print(
                f"[{index}/{total_lines}] Processing file util/downloadPapers/LaTeX/{semantic_scholar_data['title']}.zip"
            )

            pdf_path = f"util/downloadPapers/PDF/{semantic_scholar_data['title']}.pdf"
            latex_path = (
                f"util/downloadPapers/LaTeX/{semantic_scholar_data['title']}.tar.gz"
            )

            # Unzip the LaTeX project to a temporary directory
            with tempfile.TemporaryDirectory() as tempdir:
                try:
                    with tarfile.open(latex_path, "r:gz") as tar:
                        tar.extractall(tempdir)

                    paper_stats = paperStats.paperStats(pdf_path, tempdir)

                except FileNotFoundError:
                    print(
                        f"{colorama.Fore.YELLOW}Fichier non trouvé : {semantic_scholar_data['title']}{colorama.Style.RESET_ALL}"
                    )
                    continue

                except tarfile.ReadError:
                    print(
                        f"{colorama.Fore.RED}Erreur de décompression GZIP : {semantic_scholar_data['title']}{colorama.Style.RESET_ALL}"
                    )
                    continue

                except UnicodeDecodeError:
                    print(
                        f"{colorama.Fore.RED}Erreur de décodage Unicode : {semantic_scholar_data['title']}{colorama.Style.RESET_ALL}"
                    )
                    continue

            filtered_semantic_scholar_data = filterDatabaseEntryKeys(
                semantic_scholar_data
            )
            both_stats = filtered_semantic_scholar_data | paper_stats

            all_stats[index] = both_stats

        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON sur la ligne {index}: {line}")
            continue

    return all_stats


def write_csv(stats):
    """
    Stats is a dictionary of dictionaries. Each dictionary is a paper's stats.
    keys are indexes of the paper in the database.
    values are dictionaries of the paper's stats.
    """

    with open(output, "w", newline="") as csvfile:
        fieldnames = stats[0].keys()

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for index, paper in stats.items():
            writer.writerow(paper)


write_csv(get_stats())
