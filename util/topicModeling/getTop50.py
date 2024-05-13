import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


# Fonction pour extraire le texte à partir d'un fichier PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with open(pdf_file, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text


# Fonction pour obtenir les 10 mots les plus utilisés dans un papier avec LDA
def get_top_words_with_lda(text):
    stop_words = set(stopwords.words('english'))
    custom_stop_words = set(["et", "al", "search", "benchmark", "method", "study",
                             "figure", "cell", "methods", "architecture", "softmax",
                             "conference", "new"])
    stop_words = stop_words.union(custom_stop_words)

    # Ajouter les mots composés uniquement de chiffres
    words = word_tokenize(text)
    numeric_words = set([word for word in words if any(char.isdigit() for char in word)])
    stop_words = stop_words.union(numeric_words)

    vectorizer = CountVectorizer(stop_words=list(stop_words), max_features=1000)
    X = vectorizer.fit_transform([text])
    lda = LatentDirichletAllocation(n_components=1, random_state=42)
    lda.fit(X)
    feature_names = vectorizer.get_feature_names_out()
    sorted_indices = lda.components_[0].argsort()[::-1]
    top_words = [feature_names[idx] for idx in sorted_indices[:10]]
    return top_words


# Fonction pour afficher les mots les plus utilisés sous forme de diagramme à barres
def plot_top_words(top_words):
    plt.figure(figsize=(8, 5))
    plt.barh(range(len(top_words)), top_words, color='skyblue')
    plt.xlabel('Nombre d\'occurrences')
    plt.ylabel('Mots')
    plt.title('Top 10 des mots les plus utilisés dans le papier')
    plt.gca().invert_yaxis()
    plt.show()


# Exemple d'utilisation
if __name__ == "__main__":
    pdf_file = "2306.06852v1.pdf"  # Spécifiez le chemin vers votre fichier PDF
    text = extract_text_from_pdf(pdf_file)
    top_words = get_top_words_with_lda(text)
    plot_top_words(top_words)
