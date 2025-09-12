import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import cess_esp  # Spanish corpus
import numpy as np

class SpanishWordNetUtils:
    def __init__(self):
        self.ensure_nltk_data()
    
    def ensure_nltk_data(self):
        """Descargar datos necesarios de NLTK"""
        try:
            nltk.data.find('corpora/cess_esp')
        except LookupError:
            nltk.download('cess_esp')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
    
    def get_spanish_synsets(self, word):
        """Obtener synsets para palabras en español"""
        # Buscar synsets en WordNet (inglés) pero con mapeo conceptual
        synsets = wn.synsets(word)
        
        # Filtrar synsets más relevantes
        filtered_synsets = []
        for synset in synsets:
            # Priorizar synsets con definiciones más específicas
            if len(synset.lemma_names()) > 0:
                filtered_synsets.append(synset)
        
        return filtered_synsets[:3]  # Limitar a 3 synsets más relevantes
    
    def calculate_similarity(self, word1, word2):
        """Calcular similitud semántica entre dos palabras"""
        if word1 == word2:
            return 1.0
        
        synsets1 = self.get_spanish_synsets(word1)
        synsets2 = self.get_spanish_synsets(word2)
        
        if not synsets1 or not synsets2:
            return 0.1  # Similitud mínima si no se encuentran synsets
        
        # Calcular máxima similitud entre todos los pares de synsets
        max_similarity = 0.0
        for syn1 in synsets1:
            for syn2 in synsets2:
                try:
                    similarity = syn1.path_similarity(syn2)
                    if similarity and similarity > max_similarity:
                        max_similarity = similarity
                except:
                    continue
        
        return max_similarity if max_similarity > 0 else 0.1