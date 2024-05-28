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
import csv
import colorama
import concurrent.futures
import re
import os
from util.paperStats import paperStats

# List of database files
databases = [
    "util/downloadPapers/database_ICML_2020.json",
]

# Output CSV file name
output = "STATS2020.csv"

# Function to filter the relevant keys from the database entry
def filterDatabaseEntryKeys(entry):
    return {
        "corpusid": entry["corpusid"],
        "arxiv_id": entry["externalids"].get("ArXiv", ""),
        "title": entry["title"],
        "year": entry["year"],
        "venue": entry["venue"],
        "citationcount": entry["citationcount"],
        "referencecount": entry["referencecount"],
        "influentialcitationcount": entry["influentialcitationcount"],
    }

# Function to normalize filenames by replacing invalid characters
def normalize_filename(filename):
    # Define a regex pattern for invalid characters on Windows
    invalid_chars = r'[<>:"/\\|?*]'
    # Replace invalid characters with an underscore
    normalized = re.sub(invalid_chars, '_', filename)
    return normalized

# Function to get all statistics by processing in parallel
def get_all_stats(k=5):
    all_stats = {}
    lines = []

    # Read all lines from the database files
    for database in databases:
        with open(database, "r") as f:
            lines += f.readlines()

    # Split the lines into k parts
    lines_parts = [lines[i::k] for i in range(k)]

    # Process each part in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(get_stats, part, i) for i, part in enumerate(lines_parts)
        ]
        for future in concurrent.futures.as_completed(futures):
            all_stats.update(future.result())

    return all_stats

# Function to process a batch of lines and extract statistics
def get_stats(lines, process_id=0):
    total_lines = len(lines) - 1
    result = {}

    # Iterate over each line in the batch
    for index, line in enumerate(lines, start=0):
        try:
            semantic_scholar_data = json.loads(line)
            title = semantic_scholar_data['title']
            normalized_title = normalize_filename(title)
            print(
                f"[p{process_id}] [{index}/{total_lines}] Processing file util/downloadPapers/LaTeX/{normalized_title}.tar.gz"
            )

            pdf_path = f"util/downloadPapers/PDF/{normalized_title}.pdf"
            latex_path = f"util/downloadPapers/LaTeX/{normalized_title}.tar.gz"

            # Unzip the LaTeX project to a temporary directory
            with tempfile.TemporaryDirectory() as tempdir:
                try:
                    with tarfile.open(latex_path, "r:gz") as tar:
                        tar.extractall(tempdir)

                    # Extract statistics using paperStats module
                    paper_stats = paperStats.paperStats(pdf_path, tempdir)

                except FileNotFoundError:
                    print(
                        f"{colorama.Fore.YELLOW}File not found: {semantic_scholar_data['title']}{colorama.Style.RESET_ALL}"
                    )
                    continue

                except tarfile.ReadError:
                    print(
                        f"{colorama.Fore.RED}GZIP decompression error: {semantic_scholar_data['title']}{colorama.Style.RESET_ALL}"
                    )
                    continue

                except UnicodeDecodeError:
                    print(
                        f"{colorama.Fore.RED}Unicode decoding error: {semantic_scholar_data['title']}{colorama.Style.RESET_ALL}"
                    )
                    continue

            filtered_semantic_scholar_data = filterDatabaseEntryKeys(
                semantic_scholar_data
            )
            both_stats = {**filtered_semantic_scholar_data, **paper_stats}

            result[index] = both_stats

        except json.JSONDecodeError:
            print(f"JSON decoding error on line {index}: {line}")
            continue

    return result

# Function to write the statistics to a CSV file
def write_csv(stats):
    """
    Stats is a dictionary of dictionaries. Each dictionary is a paper's stats.
    keys are indexes of the paper in the database.
    values are dictionaries of the paper's stats.
    """
    with open(output, "w", newline="") as csvfile:
        if stats:
            fieldnames = next(iter(stats.values())).keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for index, paper in stats.items():
                writer.writerow(paper)

# Run the process and write the results to the CSV file
write_csv(get_all_stats())

