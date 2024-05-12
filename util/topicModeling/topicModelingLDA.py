import pandas as pd
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim.models import CoherenceModel
import nltk
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *

nltk.download("wordnet")
nltk.download("omw-1.4")

stemmer = SnowballStemmer("english")


def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos="n"))


def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result


processed_docs = [preprocess(doc) for doc in data]

dictionary = gensim.corpora.Dictionary(processed_docs)
dictionary.filter_extremes(no_below=15, no_above=0.1, keep_n=1000)
bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

lda_model = gensim.models.LdaMulticore(
    bow_corpus, num_topics=10, id2word=dictionary, passes=1000
)
topics = []
for idx, topic in lda_model.print_topics(-1):
    print("Topic: {} -> Words: {}".format(idx, topic))
    topics.append(topic)

coherence_model_lda = CoherenceModel(
    model=lda_model, texts=processed_docs, dictionary=dictionary
)
coherence_lda = coherence_model_lda.get_coherence()
print("Coherence Score: ", coherence_lda)

all_topic_model = []
for i in range(len(topics)):
    str = topics[i].split(" + ")
    topic_model = []
    for j in range(10):
        weight = str[j][0:5]
        word = str[j][7 : len(str[j]) - 1]
        topic_model.append((weight, word))
    all_topic_model.append(topic_model)
df_topic_model = pd.DataFrame(all_topic_model)
df_topic_model.rename(
    index={
        0: "Topic 1",
        1: "Topic 2",
        2: "Topic 3",
        3: "Topic 4",
        4: "Topic 5",
        5: "Topic 6",
        6: "Topic 7",
        7: "Topic 8",
        8: "Topic 9",
        9: "Topic 10",
    }
)

import pyLDAvis.gensim_models

pyLDAvis.enable_notebook()
pyLDAvis.gensim_models.prepare(lda_model, bow_corpus, dictionary)
