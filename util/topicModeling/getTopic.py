from bertopic import BERTopic
from sklearn.datasets import fetch_20newsgroups
import os
from PyPDF2 import PdfReader
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
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

    with open("docs_dl.txt", "wb") as fp:   #Pickling
        pickle.dump(docs, fp)
    return docs

def model_train():
    with open("docs_dl.txt", "rb") as fp:   # Unpickling
        docs_dl = pickle.load(fp)

    if not os.path.exists("DF_bertopic.txt"):
        vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words="english")
        topic_model = BERTopic(vectorizer_model=vectorizer_model)
        topics, probs = topic_model.fit_transform(docs_dl)

        with open("DF_bertopic.txt","wb") as fp:
            pickle.dump(topic_model,fp)

    else : 
        with open("DF_bertopic.txt","rb") as fp:
            topic_model=pickle.load(fp) 
    
    return topic_model,docs_dl


def csv_gen(topic_model):
    df=topic_model.get_topic_info()
    df.to_csv('BERTopic_output.csv',index=False)


def gen_heatmap(topic_model):
    fig=topic_model.visualize_heatmap(n_clusters=20)
    fig.write_image("visualize_topic/heat_map.png")

def gen_visualize_documents(topic_model,docs_dl):
    fig=topic_model.visualize_documents(docs_dl,
                                        topics=list(range(30)),
                                        height=600)
    fig.write_image("visualize_topic/visualize_docs.png")

if __name__=="__main__":
    topic_model,docs_dl=model_train()
    #gen_heatmap(topic_model)
    gen_visualize_documents(topic_model,docs_dl)

