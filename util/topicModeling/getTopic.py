from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups
import os
from PyPDF2 import PdfReader
import pickle
import pandas as pd
#os.environ["TOKENIZERS_PARALLELISM"] = "false"

pdf_folder = '/media/gad/D231-2070/PDF'

def docsMaker(pdf_folder):
    docs=[]
    # Parcourt tous les fichiers et dossiers dans le dossier donné
    pdfs=os.listdir(pdf_folder)
    count=0
    for pdf in pdfs:
        print(f"  Fichier {count}: {pdf}")
        reader = PdfReader(pdf_folder+'/'+pdf)
        all_text = ""
        for page in reader.pages:
            all_text += page.extract_text() + " "
        docs.append(all_text)
        count +=1

    with open("docs_dl", "wb") as fp:   #Pickling
        pickle.dump(docs, fp)
    return docs

#docs = docsMaker(pdf_folder)
with open("docs_dl", "rb") as fp:   # Unpickling
       docs_dl = pickle.load(fp)

topic_model = BERTopic()
topics, probs = topic_model.fit_transform(docs_dl)

print(len(docs_dl))
df=topic_model.get_topic_info()
del df['Representative_Docs']

df.to_csv('BERTopic_output.csv',index=False)