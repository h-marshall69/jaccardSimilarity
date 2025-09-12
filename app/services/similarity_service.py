import pandas as pd
import numpy as np
from sklearn.metrics import jaccard_score
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt
import seaborn as sns
import os
from flask import current_app
from app.utils.nltk_utils import SpanishWordNetUtils

class SimilarityService:
    def __init__(self):
        self.wordnet_utils = SpanishWordNetUtils()
    
    def load_dataset(self, filepath):
        """Cargar el dataset CSV"""
        try:
            df = pd.read_csv(filepath)
            return df, None
        except Exception as e:
            return None, f"Error cargando el dataset: {str(e)}"
    
    def preprocess_data(self, df):
        """Preprocesar los datos para análisis de similitud"""
        # Obtener todas las categorías únicas
        all_categories = set()
        for col in df.columns[1:]:  # Saltar la primera columna (usuarios)
            for categories in df[col].dropna():
                if isinstance(categories, str):
                    all_categories.update([cat.strip() for cat in categories.split(',')])
        
        # Crear matriz binaria de categorías
        binary_matrix = []
        for _, row in df.iterrows():
            user_categories = set()
            for col in df.columns[1:]:
                if pd.notna(row[col]):
                    user_categories.update([cat.strip() for cat in str(row[col]).split(',')])
            
            binary_row = [1 if cat in user_categories else 0 for cat in all_categories]
            binary_matrix.append(binary_row)
        
        return pd.DataFrame(binary_matrix, columns=list(all_categories)), list(all_categories)
    
    def calculate_jaccard_similarity(self, binary_matrix):
        """Calcular matriz de similitud de Jaccard"""
        jaccard_sim = 1 - pdist(binary_matrix, metric='jaccard')
        jaccard_matrix = squareform(jaccard_sim)
        return jaccard_matrix
    
    def calculate_semantic_similarity(self, categories):
        """Calcular similitud semántica usando WordNet español"""
        n_categories = len(categories)
        semantic_matrix = np.zeros((n_categories, n_categories))
        
        for i in range(n_categories):
            for j in range(n_categories):
                if i == j:
                    semantic_matrix[i][j] = 1.0
                else:
                    similarity = self.wordnet_utils.calculate_similarity(
                        categories[i], categories[j]
                    )
                    semantic_matrix[i][j] = similarity
        
        return semantic_matrix
    
    def create_heatmap(self, matrix, labels, title, filename):
        """Crear heatmap de similitud"""
        plt.figure(figsize=(12, 10))
        sns.heatmap(matrix, xticklabels=labels, yticklabels=labels,
                   cmap='viridis', annot=True, fmt='.2f')
        plt.title(title, fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        # Guardar imagen
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        plt.savefig(image_path)
        plt.close()
        
        return image_path
    
    def create_dendrogram(self, matrix, labels, filename):
        """Crear dendrograma"""
        plt.figure(figsize=(15, 8))
        linked = linkage(matrix, method='ward')
        
        dendrogram(linked,
                  orientation='top',
                  labels=labels,
                  distance_sort='descending',
                  show_leaf_counts=True)
        
        plt.title('Dendrograma de Similitud', fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Guardar imagen
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        plt.savefig(image_path)
        plt.close()
        
        return image_path
    
    def process_dataset(self, filepath):
        """Procesar completo del dataset"""
        # Cargar datos
        df, error = self.load_dataset(filepath)
        if error:
            return None, error
        
        # Preprocesar
        binary_matrix, categories = self.preprocess_data(df)
        
        # Calcular similitudes
        jaccard_matrix = self.calculate_jaccard_similarity(binary_matrix.values)
        semantic_matrix = self.calculate_semantic_similarity(categories)
        
        # Crear visualizaciones
        results = {
            'original_data': df.to_dict('records'),
            'categories': categories,
            'binary_matrix': binary_matrix.values.tolist(),
            'jaccard_matrix': jaccard_matrix.tolist(),
            'semantic_matrix': semantic_matrix.tolist(),
            'users': df.iloc[:, 0].tolist()  # Nombres de usuarios
        }
        
        # Generar imágenes
        try:
            results['jaccard_heatmap'] = self.create_heatmap(
                jaccard_matrix, results['users'], 
                'Matriz de Similitud de Jaccard (Usuarios)', 'jaccard_heatmap.png'
            )
            
            results['semantic_heatmap'] = self.create_heatmap(
                semantic_matrix, categories,
                'Matriz de Similitud Semántica (Categorías)', 'semantic_heatmap.png'
            )
            
            results['dendrogram'] = self.create_dendrogram(
                jaccard_matrix, results['users'], 'dendrogram.png'
            )
            
        except Exception as e:
            print(f"Error creating visualizations: {e}")
            # Continuar sin imágenes si hay error
        
        return results, None