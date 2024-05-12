import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict

# Fonction pour extraire le texte à partir d'un fichier PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

# Fonction pour nettoyer et prétraiter le texte
def preprocess_text(text):
    # Tokenization
    tokens = word_tokenize(text)
    # Suppression de la ponctuation
    tokens = [word.lower() for word in tokens if word.isalpha()]
    return ' '.join(tokens)

# Fonction pour appliquer le modèle de topic modeling (NMF)
def apply_nmf_model(text, num_topics=5):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([text])
    nmf = NMF(n_components=num_topics, random_state=42)
    nmf.fit(X)
    return nmf, vectorizer

# Fonction pour obtenir les sujets les plus traités
def get_top_topics(nmf_model, vectorizer, top_n=3):
    feature_names = vectorizer.get_feature_names_out()
    topics = nmf_model.components_
    top_topics = []
    for topic_idx in range(len(topics)):
        topic_words = [feature_names[i] for i in topics[topic_idx].argsort()[:-top_n - 1:-1]]
        top_topics.append(topic_words)
    return top_topics

# Fonction principale
def main(pdf_file):
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
    pdf_file = "2403.06080v1.pdf"  # Spécifiez le chemin vers votre fichier PDF
    top_topics = main(pdf_file)
    print("Top 3 sujets les plus traités :")
    for idx, topic in enumerate(top_topics[:3]):
        print(f"Sujet {idx + 1}: {', '.join(topic)}")
