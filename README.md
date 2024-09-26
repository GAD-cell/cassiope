Project Cassiopée 2023-2024
Axel Benadiba, Sinoué Gad, Paul Guilloux

## Objective
When scientists want to present a result, they write a scientific paper. These papers are highly structured: they often follow the same format, must be well presented, free of errors, and of appropriate length, etc.

Meeting these standards is important because the papers are evaluated by the community to determine if they should be presented at a conference, which is the ultimate goal. Beyond scientific criteria, aspects related to presentation can have a significant impact. It is always unfortunate to fail due to an issue that could have been easily corrected.

In this project, we propose building a tool capable of evaluating a scientific paper to correct the most obvious errors and suggest improvement ideas. The user interface will be web-based, but the server can be coded in any language.

## The project steps are as follows:

Converting papers from PDF format into a more structured format. Papers are often written in LaTeX, but only the PDF is shared. We need to be able to restructure the PDF.
Data analysis on existing papers. We will consult a database of previously written papers to extract common rules found in the most popular articles. These rules will then be added to the final system.
Implementation of the verification system. Given an article, we want to generate a list of possible improvements and corrections.
Creation of an interface. A user should be able to interact with our tool via a web interface.
Project Components
### 1. Data Download: util/downloadPapers
The downloadPapers.py script allows downloading scientific papers from the arXiv website. It takes a list of keywords as input and downloads the corresponding papers.

Initially, it generates a database using SemanticScholar based on the search criteria. Then, it downloads the corresponding papers.

We retrieve the following:

The paper in PDF format
The LaTeX sources in .tar.gz format
### 2. Metric Extraction: util/paperStats
The paperStats.py module takes a paper (PDF+LaTeX) as input and extracts metrics. These metrics are information about the paper, such as the number of words, figures, references, etc.

All this data is saved in a STATS.csv spreadsheet, which is kept up to date in this repository.

### 3. Data Analysis: util/paperStats/featureStats
The featureStats.py script takes the STATS.csv file as input and extracts statistics. These statistics provide information on the extracted metrics, such as the mean, standard deviation, and correlations between different metrics.

### 4. Topic Analysis: util/topicModeling
The getTopic.py module performs topic modeling on the articles using BERTopic. It analyzes all the PDFs and extracts topics from them.

### 5. User Interface: web
The web folder contains the user interface. It allows users to upload a paper, submit it for analysis, and retrieve the results. To launch it: ./start.sh



![img](/.github/webapp.png)
