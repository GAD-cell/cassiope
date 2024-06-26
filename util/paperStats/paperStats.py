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
- Number of figures
- Number of tables
- Number of equations
- Number of references and citations
- Number of grammar errors

"""

from collections import Counter
import argparse
import fitz
import json
import os
import re

# Import the topicModeling module, located at ../topicModeling
# import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "topicModeling"))

# import topicModeling

""" tool = language_tool_python.LanguageTool(
    "en-US", config={"cacheSize": 1000, "pipelineCaching": True}
) """

# Define the parser
parser = argparse.ArgumentParser(description="Infer statistics about a pdf.")
parser.add_argument("pdf", help="Path to the pdf file.")
parser.add_argument("latex", help="Path to the latex project directory.")


# Process the latex project and return one big latex text file
def parse_latex(latex_dir):
    """
    Inside the latex project directory, we want to do the following:
    - Find the main tex file. This is the file that contains `documentclass`.
    - Find all the tex files that are included in the main file.
    - Replace all the references with the actual text.
    - Return the project as one big latex string.
    """

    # Find all the tex files that are included in the main file
    included_tex_files = []

    # Add ALL .tex files in the directory (recursively)
    for root, dirs, files in os.walk(latex_dir):
        for file in files:
            if file.endswith(".tex"):
                included_tex_files.append(file)

    latex = ""

    for tex_file in included_tex_files:
        try:
            with open(os.path.join(latex_dir, tex_file), "r") as f:
                latex += f.read()
        except:
            continue

    # Remove comments
    latex = re.sub(r"%.*", "", latex)

    # Remove excess line breaks
    latex = re.sub(r"\n+", "\n", latex)

    return latex


# Util : get the number of occurrences of regex matches in a string, among an array of regexes
def get_number_occurences(string, regexes):
    count = 0
    for regex in regexes:
        count += len(re.findall(regex, string))
    return count


def get_number_pages(doc):
    return doc.page_count


def get_number_words(doc):
    words = [word for page in doc for word in page.get_text("text").split()]
    return len(words)


def get_font(doc):
    try:
        font_counter = Counter()
        for page in doc:
            for font in page.get_fonts():
                font_counter[font[3]] += 1

        most_common_font = font_counter.most_common(1)[0][0]

        return most_common_font.split("+")[1].split("-")[0]
    except:
        return "Unknown"


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

def get_abstract_length(latex):
    abstract_match = re.search(r'\\begin{abstract}(.*?)\\end{abstract}', latex, re.DOTALL)
    if abstract_match:
        abstract = abstract_match.group(1).strip()
        return len(abstract.split(" "))
    else:
        return 0

def get_acronyms(pdf_path):
    title = os.path.basename(pdf_path).split("/")[-1].split(".")[0]
    title = title.replace("_", " ")
    return re.search(r'\b[A-Z]{2,}\b', title) is not None

def get_title_length(pdf_path):
    return len(os.path.basename(pdf_path).split("/")[-1].split(".")[0])

def get_authors(latex):
    author_section = re.search(r'\\author\{(.+?)\}', latex, re.DOTALL)
    if not author_section:
        return 0
    authors = author_section.group(1)
    authors = re.sub(r'\\thanks\{.*?\}', '', authors)
    return len(re.findall(r'\\and', authors)) + 1


""" def get_grammar_errors(latex_dir):

    # Ignore errors on uppercase or titlecase words
    is_bad_match = (
        lambda rule: rule.message == "Possible spelling mistake found."
        and len(rule.replacements)
        and (rule.replacements[0][0].isupper() or rule.replacements[0][0].istitle())
    )

    try:
        main_tex = get_main_latex_file(latex_dir, local=False)
        text = pypandoc.convert_file(
            main_tex, "plain", format="latex", extra_args=["--wrap=nonec --verbose=0"]
        )
    except RuntimeError:
        # If pandoc fails to convert the file, return 0
        return 0

    matches = tool.check(text)
    matches = [match for match in matches if not is_bad_match(match)]

    return len(matches) """


""" def getTopics(doc):
    return topicModeling.topicModeling(doc)[0] """


def paperStats(pdf_path, latex_dir):

    pdf = fitz.open(pdf_path)
    latex = parse_latex(latex_dir)

    # topic1, topic2, topic3 = getTopics(pdf_path)

    STATS = {
        "abstract_length": get_abstract_length(latex),
        "acronym_presence": get_acronyms(pdf_path),
        "authors": 8, #get_authors(latex),
        "content_references": get_references(latex) + get_citations(latex),
        "equations": get_equations(latex),
        "figures": get_figures(latex),
        "font": get_font(pdf),
        "pages": get_number_pages(pdf),
        "paragraphs": get_paragraphs(latex),
        "sections": get_sections(latex),
        "subsections": get_subsections(latex),
        "subsubsections": get_subsubsections(latex),
        "tables": get_tables(latex),
        "title_length": get_title_length(pdf_path),
        "words": get_number_words(pdf),
    }

    return STATS


if __name__ == "__main__":

    # Parse the arguments
    args = parser.parse_args()
    pdf_path = args.pdf

    STATS = paperStats(pdf_path, args.latex)
    print(json.dumps(STATS, indent=4))
