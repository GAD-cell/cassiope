import time
from flask import Flask, request
import tempfile
import zipfile

from .paperStats import paperStats

app = Flask(__name__)


@app.route("/time")
def get_current_time():
    return {"time": time.time()}

@app.route("/paper-stats", methods=["POST"])
def get_paper_stats():
    pdf = request.files["pdf"]
    latex_zip = request.files["latex"]

    with tempfile.TemporaryDirectory() as tempdir:
        # PDF : single file
        # LaTeX : directory unzipped from latex_zip

        pdf_path = f"{tempdir}/paper.pdf"
        latex_path = f"{tempdir}/latex"

        pdf.save(pdf_path)

        with zipfile.ZipFile(latex_zip, "r") as zip_ref:
            zip_ref.extractall(latex_path)

        STATS = paperStats(pdf_path, latex_path)

    return STATS
