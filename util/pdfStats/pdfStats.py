"""
Reads a research paper and infers statistics about it.

Arguments :
- pdf file
- latex project directory

For now, it prints the following statistics:

- Number of pages
- Number of words
- Number of paragraphs
- Font
- Number of citations

"""

import os
import re
import sys
import fitz
import json
import string
import argparse
import numpy as np
from collections import Counter

# Define the parser
parser = argparse.ArgumentParser(description="Infer statistics about a pdf.")
parser.add_argument("pdf", help="Path to the pdf file.")
parser.add_argument("latex", help="Path to the latex project directory.")

# Parse the arguments
args = parser.parse_args()
pdf_path = args.pdf

# Open the pdf
doc = fitz.open(pdf_path)


def parse_latex(latex_dir):
    """
    Inside the latex project directory, we want to do the following:
    - Find the main tex file. This is the file that contains `documentclass`.
    - Find all the tex files that are included in the main file.
    - Replace all the references with the actual text.
    - Return the project as one big latex string.
    """

    # Find the main text file
    main_tex = None
    for root, dirs, files in os.walk(latex_dir):
        for file in files:
            if file.endswith(".tex"):
                with open(os.path.join(root, file), "r") as f:
                    if "documentclass" in f.read():
                        main_tex = os.path.join(root, file)
                        break
        if main_tex:
            print(f"Main tex file found: {main_tex}")
            break

    if not main_tex:
        raise ValueError("No main tex file found.")

    # Find all the tex files that are included in the main file
    included_tex_files = []
    with open(main_tex, "r") as f:
        for line in f:
            if "input" in line or "include" in line:
                if ".tex" in line:
                    included_tex_files.append(line.split("{")[1].split("}")[0])

    print(f"Included tex files: {included_tex_files}")

    # Replace all the references with the actual text
    latex = main_tex
    for tex_file in included_tex_files:
        with open(os.path.join(latex_dir, tex_file), "r") as f:
            latex += f.read()

    # Remove comments
    latex = re.sub(r"%.*", "", latex)

    # Remove excess line breaks
    latex = re.sub(r"\n\n+", "\n", latex)

    return latex


latex = parse_latex(args.latex)

print(latex)


def get_number_pages(doc):
    return doc.page_count


def get_number_words(doc):
    words = []
    for page in doc:
        words += page.get_text("text").split()
    return len(words)


def get_font(doc):
    fonts = []
    for page in doc:
        fonts += page.get_fonts()

    return Counter(fonts).most_common(1)[0][0][3]


def get_citations(doc):
    citations = 0
    for page in doc:
        citations += len(re.findall(r"\[\d+\]", page.get_text("text")))
    return citations


STATS = {
    "pages": get_number_pages(doc),
    "words": get_number_words(doc),
    "font": get_font(doc),
    "citations": get_citations(doc),
}

print(json.dumps(STATS, indent=4))
