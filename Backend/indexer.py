from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Liste simple de stopwords français (extensible)
FRENCH_STOPWORDS = [
    "le", "la", "les", "un", "une", "des",
    "et", "ou", "de", "du", "dans", "sur",
    "à", "au", "aux", "en", "pour", "par",
    "avec", "sans", "est", "sont", "être",
    "plus", "moins", "très", "peu"
]
class TextIndexer:
    """
    Classe responsable de :
    - vectorisation TF-IDF
    - calcul de similarité cosinus
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words=FRENCH_STOPWORDS,
            max_features=500
        )
        self.documents = []
        self.vectors = None

    def add_documents(self, docs):
        """
        Ajoute des documents et calcule les vecteurs TF-IDF
        """
        # Sécurité : supprimer documents vides
        self.documents = [doc for doc in docs if doc.strip() != ""]

        if not self.documents:
            return

        self.vectors = self.vectorizer.fit_transform(self.documents)

    def search(self, query, top_k=2):
        """
        Recherche les documents les plus proches
        de la requête utilisateur
        """
        if self.vectors is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.vectors)[0]

        # Trier par similarité décroissante
        ranked_indices = similarities.argsort()[::-1][:top_k]

        return [self.documents[i] for i in ranked_indices]
















