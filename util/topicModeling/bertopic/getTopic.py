from bertopic import BERTopic
import os
from PyPDF2 import PdfReader
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
#os.environ["TOKENIZERS_PARALLELISM"] = "false"
import plotly.io as pio
import csv
import sys


pdf_folder = '/home/gad/Documents/PDF'

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

def hash_maker():
    hashmap={}
    pdfs=os.listdir(pdf_folder)
    pdfs=remove_pdf_suffix(pdfs)
    with open("docs_dl.txt", "rb") as fp:   # Unpickling
        docs_dl = pickle.load(fp)
    fichier=0
    for doc in docs_dl:
        hashmap[doc]=pdfs[fichier]
        fichier +=1

    return hashmap

def remove_pdf_suffix(pdf_list):
    return [filename[:-4] if filename.endswith(".pdf") else filename for filename in pdf_list]
     
def get_representative_docs(representative_docs,hashmap):
    docs=[]
    for doc in representative_docs:
        docs.append(hashmap[doc])
    return docs

def representative_docs_gen(topic_model):
    csv.field_size_limit(sys.maxsize)
    hashmap=hash_maker()
    representative_docs=csv_gen(topic_model)
    docs=[]
    for representative in representative_docs:
        docs.append(get_representative_docs(representative,hashmap))
    
    input_file = 'BERTopic_output.csv'
    output_file = 'BERTopic_modified.csv'

    with open(input_file, mode='r', newline='') as infile, open(output_file, mode='w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        header = next(reader) 
        writer.writerow(header)
        for i, row in enumerate(reader):
            if i < len(docs):
                if len(row) > 4:  
                    row[4] = docs[i]
                else:  # Ajoute des colonnes vides si nécessaire pour atteindre la 5ème colonne
                    row.extend([''] * (5 - len(row)))
                    row[4] = docs[i]
            writer.writerow(row)

    print(f"Le fichier CSV a été mis à jour et enregistré sous le nom {output_file}.")


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
    if not os.path.exists("BERTopic_output.csv"):
        df.to_csv('BERTopic_output.csv',index=False)
    representative_docs= df["Representative_Docs"]
    return representative_docs



def gen_heatmap(topic_model):
    fig=topic_model.visualize_heatmap(n_clusters=20)
    fig.write_image("visualize_topic/heat_map.png")

def gen_visualize_documents(topic_model,docs_dl):
    fig=topic_model.visualize_documents(docs_dl,
                                        topics=list(range(30)),
                                        height=600)
    #pio.write_image(fig, "visualize_topic/output.png", engine="kaleido")
    fig.show()



if __name__=="__main__":
    topic_model,docs_dl=model_train()
    representative_docs_gen(topic_model)
    
    #gen_heatmap(topic_model)
    #gen_visualize_documents(topic_model,docs_dl)

