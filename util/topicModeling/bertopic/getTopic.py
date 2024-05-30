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
import nltk
from nltk.corpus import stopwords
import numpy as np

# Télécharger les stopwords de nltk si ce n'est pas déjà fait
nltk.download('stopwords')

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

def representative_docs_gen(topic_model,representative_docs):
    csv.field_size_limit(sys.maxsize)
    hashmap=hash_maker()
    #representative_docs=csv_gen(topic_model)
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
    custom_stopwords = set(stopwords.words('english'))
    custom_stopwords.update(["al","et","et al"])
    custom_stopwords = list(custom_stopwords)

    with open("docs_dl.txt", "rb") as fp:   # Unpickling
        docs_dl = pickle.load(fp)
    if not os.path.exists("DF_bertopic.txt"):
        vectorizer_model = CountVectorizer( stop_words=custom_stopwords)
        topic_model = BERTopic(vectorizer_model=vectorizer_model)
        topics, probs = topic_model.fit_transform(docs_dl)
        
        nr_docs = 5
        # Obtenir les documents représentatifs manuellement
        representative_docs = []
        for topic in set(topics):
            topic_docs = np.array(docs_dl)[np.array(topics) == topic]
            doc_probs = np.array(probs)[np.array(topics) == topic]
            
            # Trier les documents par leur score de probabilité décroissante
            top_indices = doc_probs.argsort()[-nr_docs:][::-1]
            representative_docs.append(topic_docs[top_indices])
        
        with open("Representative_topic.txt","wb") as fp:
            pickle.dump(representative_docs,fp)
        
        with open("DF_bertopic.txt","wb") as fp:
            pickle.dump(topic_model,fp)

    else : 
        with open("DF_bertopic.txt","rb") as fp:
            topic_model=pickle.load(fp) 
        with open("Representative_topic.txt","rb") as fp:
            representative_docs=pickle.load(fp) 
    
    return topic_model,docs_dl,representative_docs


def csv_gen(topic_model):
    df=topic_model.get_topic_info()
    if not os.path.exists("BERTopic_output.csv"):
        df.to_csv('BERTopic_output.csv',index=False)
    representative_docs= df["Representative_Docs"]
    return representative_docs



def gen_heatmap(topic_model):
    fig=topic_model.visualize_heatmap(n_clusters=20)
    fig.write_image("/home/gad/Documents/cassiope/cassiope/util/topicModeling/visualize_topic/heat_map.png")

def gen_visualize_documents(topic_model,docs_dl):
    fig=topic_model.visualize_documents(docs_dl,
                                        topics=list(range(30)),
                                        height=600)
    #pio.write_image(fig, "visualize_topic/output.png", engine="kaleido")
    fig.show()



if __name__=="__main__":
    topic_model,docs_dl,representative_docs=model_train()
    #csv_gen(topic_model)
    #representative_docs_gen(topic_model,representative_docs)
    
    #gen_heatmap(topic_model)
    gen_visualize_documents(topic_model,docs_dl)

