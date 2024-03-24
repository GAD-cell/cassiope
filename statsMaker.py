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


with open(database, "r") as file:
    lines = file.readlines()

    # Itération sur chaque ligne du fichier JSON
    for index, line in enumerate(lines, start=0):
        try:
            semantic_scholar_data = json.loads(line)

            print(
                f"Processing file util/downloadPapers/LaTeX/{semantic_scholar_data['title']}.zip"
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

                except FileNotFoundError:
                    continue

                paper_stats = paperStats.paperStats(pdf_path, tempdir)

            filtered_semantic_scholar_data = filterDatabaseEntryKeys(
                semantic_scholar_data
            )
            all_stats = filtered_semantic_scholar_data | paper_stats

            print(json.dumps(all_stats, indent=4))

        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON sur la ligne {index}: {line}")
            continue
