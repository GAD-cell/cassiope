"""
Reads a research paper and infers statistics about it.

Arguments :
- pdf file
- latex project directory

For now, it prints the following statistics:

- Number of pages
- Number of words
- Number of paragraphs
- Number of sections
- Number of subsections
- Number of subsubsections
- Font
- Number of citations
- Number of figures
- Number of tables
- Number of equations
- Number of references

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

    ## Check if main.tex exists
    if os.path.exists(os.path.join(latex_dir, "main.tex")):
        main_tex = os.path.join(latex_dir, "main.tex")
        # print(f"Main tex file found directly: {main_tex}")

    ## If not, search for the main tex file
    if not main_tex:
        for root, dirs, files in os.walk(latex_dir):
            for file in files:
                if file.endswith(".tex"):
                    with open(os.path.join(root, file), "r") as f:
                        if "documentclass" in f.read():
                            main_tex = os.path.join(root, file)
                            break
            if main_tex:
                # print(f"Main tex file found: {main_tex}")
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

    # print(f"Included tex files: {included_tex_files}")

    # Read the main tex file and all the included tex files
    with open(main_tex, "r") as f:
        latex = f.read()

    for tex_file in included_tex_files:
        with open(os.path.join(latex_dir, tex_file), "r") as f:
            latex += f.read()

    # Remove comments
    latex = re.sub(r"%.*", "", latex)

    # Remove excess line breaks
    latex = re.sub(r"\n+", "\n", latex)

    return latex


# Util : get the number of occurences of regex matches in a string, among an array of regexes
def get_number_occurences(string, regexes):
    count = 0
    for regex in regexes:
        count += len(re.findall(regex, string))
    return count


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

    # Get the most common font
    most_common_font = Counter(fonts).most_common(1)[0][0][3]

    # Font string format is like AECCXO+NimbusRomNo9L-Regu
    # We want to extract the font family
    return most_common_font.split("+")[1].split("-")[0]


def get_citations(latex):
    return get_number_occurences(
        latex,
        [
            r"\\cite",
            r"\\citep",
            r"\\citet",
            r"\\citeauthor",
            r"\\citeyear",
            r"\\citealp",
            r"\\citealt",
            r"\\citep\*",
            r"\\citeauthor\*",
            r"\\citeyear\*",
            r"\\citealp\*",
            r"\\citealt\*",
            r"\\singleemcite",
        ],
    )


def get_figures(latex):
    return get_number_occurences(
        latex, [r"\\begin{figure", r"\\begin{figure*", r"\\includegraphics"]
    )


def get_tables(latex):
    return get_number_occurences(latex, [r"\\begin{table", r"\\begin{table*"])


def get_paragraphs(latex):
    return get_number_occurences(latex, [r"\\paragraph", r"\\subparagraph"])


def get_equations(latex):
    return get_number_occurences(
        latex,
        [
            r"\\begin{equation",
            r"\\begin{equation*",
            r"\\begin{eqnarray",
            r"\\begin{eqnarray*",
            r"\\begin{align",
            r"\\begin{align*",
            r"\\begin{alignat",
            r"\\begin{alignat*",
            r"\\begin{gather",
            r"\\begin{gather*",
            r"\\begin{flalign",
            r"\\begin{flalign*",
            r"\\begin{multline",
            r"\\begin{multline*",
            r"\\begin{split",
            r"\\begin{split*",
            r"\\\[",
        ],
    )


def get_references(latex):
    return get_number_occurences(latex, [r"\\bibitem"])


def get_sections(latex):
    return get_number_occurences(latex, [r"\\section"])


def get_subsections(latex):
    return get_number_occurences(latex, [r"\\subsection"])


def get_subsubsections(latex):
    return get_number_occurences(latex, [r"\\subsubsection"])


def paperStats(pdf_path, latex_dir):

    pdf = fitz.open(pdf_path)
    latex = parse_latex(latex_dir)

    STATS = {
        "citations": get_citations(latex),
        "equations": get_equations(latex),
        "figures": get_figures(latex),
        "font": get_font(pdf),
        "pages": get_number_pages(pdf),
        "paragraphs": get_paragraphs(latex),
        "references": get_references(latex),
        "tables": get_tables(latex),
        "words": get_number_words(pdf),
        "sections": get_sections(latex),
        "subsections": get_subsections(latex),
        "subsubsections": get_subsubsections(latex),
    }

    return STATS


if __name__ == "__main__":

    # Parse the arguments
    args = parser.parse_args()
    pdf_path = args.pdf

    STATS = paperStats(pdf_path, args.latex)
    print(json.dumps(STATS, indent=4))
