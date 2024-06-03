from .paperStats import paperStats
from .topicModeling.bertopic.getTopic import get_html_topic
from flask import Flask, request
import os
import tempfile
import time
import zipfile

app = Flask(__name__)


@app.route("/time")
def get_current_time():
    return {"time": time.time()}

@app.route("/topics-graph")
def get_topics_graph():
    try:
        return {'raw_html': get_html_topic()}
    except Exception as e:
        raise e

@app.route("/paper-stats", methods=["POST"])
def get_paper_stats():

    try:

        pdf = request.files["pdf"]
        latex_zip = request.files["latex_zip"]

        with tempfile.TemporaryDirectory() as tempdir:
            # PDF : single file
            # LaTeX : directory unzipped from latex_zip

            pdf_path = f"{tempdir}/{pdf.filename}"
            latex_path = f"{tempdir}/{latex_zip.filename.split('.')[0]}"

            pdf.save(pdf_path)

            with zipfile.ZipFile(latex_zip, "r") as zip_ref:
                zip_ref.extractall(latex_path)

            STATS = paperStats.paperStats(pdf_path, latex_path)
        return STATS
    
    except Exception as e:
        return {}
