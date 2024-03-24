"""
Takes a database of papers in json format, processes them with util/paperStats/paperStats.py and outputs a CSV with the statistics of each paper.

It is expected that the paper files have been downloaded with util/Download Papers/downloadPapers.py.
PDFs should be in util/Download Papers/PDF and zipped LaTeX projets in util/Download Papers/LaTeX.
Their filesnames should be {title}.pdf and {title}.zip respectively.

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
import zipfile
from util.paperStats import paperStats

database = "util/Download Papers/database_filtered.json"
output = "STATS.csv"

with open(database, "r") as file:
    lines = file.readlines()

    # Itération sur chaque ligne du fichier JSON
    for index, line in enumerate(lines, start=0):

        try:
            paper_data = json.loads(line)

            print(
                f"Processing file util/Download Papers/LaTeX/{paper_data['title']}.zip"
            )

            pdf_path = f"util/Download Papers/PDF/{paper_data['title']}.pdf"
            latex_path = f"util/Download Papers/LaTeX/{paper_data['title']}.zip"

            # Unzip the LaTeX project to a temporary directory
            with tempfile.TemporaryDirectory() as tempdir:
                with zipfile.ZipFile(latex_path, "r") as zip_ref:
                    zip_ref.extractall(tempdir)

                # Run paperStats.py
                stats = paperStats.paperStats(pdf_path, tempdir)

                print(stats)

        except json.JSONDecodeError:
            print(f"Erreur de décodage JSON sur la ligne {index}: {line}")
            continue
