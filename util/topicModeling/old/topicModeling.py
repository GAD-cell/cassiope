import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet

MINIMUM_WORD_LENGTH = 4


# Fonction pour extraire le texte à partir d'un fichier PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with open(pdf_file, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text


def get_lemma(word):
    lemma = wordnet.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


# Fonction pour nettoyer et prétraiter le texte
def preprocess_text(text):
    # Tokenization
    tokens = word_tokenize(text)
    # Suppression de la ponctuation
    tokens = [word.lower() for word in tokens if word.isalpha()]
    # Suppression des mots courts
    tokens = [word for word in tokens if len(word) > MINIMUM_WORD_LENGTH]
    # Suppression des stopwords
    en_stop = set(stopwords.words("english"))
    tokens = [word for word in tokens if word not in en_stop]
    # Lemmatization
    tokens = [get_lemma(word) for word in tokens]
    return " ".join(tokens)


# Fonction pour appliquer le modèle de topic modeling (NMF)
def apply_nmf_model(text, num_topics=5):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([text])
    nmf = NMF(n_components=num_topics, random_state=0)
    nmf.fit(X)
    return nmf, vectorizer


# Fonction pour obtenir les sujets les plus traités
def get_top_topics(nmf_model, vectorizer, top_n=3):
    feature_names = vectorizer.get_feature_names_out()
    topics = nmf_model.components_
    top_topics = []
    for topic_idx in range(len(topics)):
        topic_words = [
            feature_names[i] for i in topics[topic_idx].argsort()[: -top_n - 1 : -1]
        ]
        top_topics.append(topic_words)
    return top_topics


# Fonction principale
def topicModeling(pdf_file):
    # Extraction du texte du PDF
    text = extract_text_from_pdf(pdf_file)
    # Prétraitement du texte
    preprocessed_text = preprocess_text(text)
    # Application du modèle de topic modeling (NMF)
    nmf_model, vectorizer = apply_nmf_model(preprocessed_text)
    # Obtention des trois sujets les plus traités
    top_topics = get_top_topics(nmf_model, vectorizer)
    return top_topics


# Exemple d'utilisation
if __name__ == "__main__":

    # Check if wordnet  and stopwords are downloaded
    import nltk

    try:
        nltk.data.find("corpora/wordnet")
    except LookupError:
        nltk.download("wordnet")

    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords")

    pdf_file = "2306.06852v1.pdf"  # Spécifiez le chemin vers votre fichier PDF
    top_topics = topicModeling(pdf_file)
    print("Top 3 sujets les plus traités :")
    for idx, topic in enumerate(top_topics[:3]):
        print(f"Sujet {idx + 1}: {', '.join(topic)}")
