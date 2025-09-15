import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import csv
from collections import defaultdict
import warnings
import json
import re
from unidecode import unidecode
import spacy
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import nltk

warnings.filterwarnings('ignore')

# Descargar recursos de NLTK si no están disponibles
try:
    nltk.download('stopwords', quiet=True)
except:
    pass

class NLPProcessor:
    """Procesador de lenguaje natural para español"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('spanish'))
        self.stemmer = SnowballStemmer('spanish')
        
        # Cargar modelo de spaCy para español si está disponible
        try:
            self.nlp = spacy.load("es_core_news_sm")
            self.spacy_available = True
        except:
            self.spacy_available = False
            print("spaCy español no disponible, usando procesamiento básico")
        
        # Diccionario de sinónimos y parónimos
        self.synonyms = self._load_synonyms()
        self.paronyms = self._load_paronyms()
    
    def _load_synonyms(self):
        """Cargar diccionario de sinónimos"""
        synonyms = {
            'ciencia_ficcion': ['scifi', 'ciencia ficcion', 'ficcion_cientifica'],
            'terror': ['miedo', 'horror', 'suspenso'],
            'comedia': ['risa', 'humor', 'divertido'],
            'drama': ['serio', 'emocional', 'intenso'],
            'accion': ['aventura', 'emocion', 'movimiento'],
            'romance': ['amor', 'pasion', 'sentimental'],
            'fantasia': ['magia', 'imaginacion', 'sobrenatural'],
            'documental': ['realidad', 'informacion', 'educativo'],
            'animacion': ['dibujos', 'cartoon', 'animado'],
            'thriller': ['suspense', 'tension', 'emocionante'],
            'musical': ['musica', 'cantos', 'baile'],
            'aventura': ['exploracion', 'viaje', 'descubrimiento'],
            'biografia': ['vida', 'historia_personal', 'real'],
            'historia': ['historico', 'epoca', 'pasado'],
            'crimen': ['delito', 'policial', 'investigacion'],
            'western': ['vaquero', 'frontera', 'oeste']
        }
        return synonyms
    
    def _load_paronyms(self):
        """Cargar diccionario de parónimos"""
        paronyms = {
            'accion': ['acion', 'accion', 'axion'],
            'comedia': ['comedia', 'comedia', 'komedia'],
            'drama': ['drama', 'drama', 'dramma'],
            'terror': ['terror', 'teror', 'terror'],
            'romance': ['romance', 'romanse', 'romance'],
            'fantasia': ['fantasia', 'fantasía', 'fantasia'],
            'ciencia_ficcion': ['ciencia_ficcion', 'ciencia ficcion', 'sci-fi'],
            'documental': ['documental', 'documental', 'documental'],
            'animacion': ['animacion', 'animación', 'animation'],
            'thriller': ['thriller', 'triller', 'suspenso'],
            'aventura': ['aventura', 'aventura', 'adventura'],
            'biografia': ['biografia', 'biografía', 'biography'],
            'historia': ['historia', 'história', 'history'],
            'musical': ['musical', 'musical', 'music'],
            'crimen': ['crimen', 'crimen', 'crime'],
            'western': ['western', 'western', 'wester']
        }
        return paronyms
    
    def preprocess_text(self, text):
        """Preprocesar texto: normalizar, eliminar stop words, etc."""
        if not isinstance(text, str):
            return text
            
        # Convertir a minúsculas y normalizar
        text = text.lower().strip()
        text = unidecode(text)  # Eliminar acentos
        text = re.sub(r'[^a-z0-9_\s]', '', text)  # Eliminar caracteres especiales
        text = re.sub(r'\s+', ' ', text)  # Eliminar espacios múltiples
        
        return text
    
    def normalize_genre(self, genre):
        """Normalizar género cinematográfico"""
        genre = self.preprocess_text(genre)
        
        # Reemplazar sinónimos
        for main_genre, synonyms in self.synonyms.items():
            if genre in synonyms or genre == main_genre:
                return main_genre
        
        # Corregir parónimos
        for main_genre, variations in self.paronyms.items():
            if genre in variations:
                return main_genre
        
        # Stemming
        stemmed = self.stemmer.stem(genre)
        for main_genre in self.synonyms.keys():
            if stemmed in [self.stemmer.stem(s) for s in [main_genre] + self.synonyms[main_genre]]:
                return main_genre
        
        return genre
    
    def is_stop_word(self, word):
        """Verificar si una palabra es stop word"""
        return word in self.stop_words or len(word) < 3
    
    def lemmatize(self, text):
        """Lematizar texto usando spaCy si está disponible"""
        if self.spacy_available:
            doc = self.nlp(text)
            return ' '.join([token.lemma_ for token in doc])
        return text

class UserPreferencesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Preferencias de Usuarios")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Inicializar procesador NLP
        self.nlp_processor = NLPProcessor()
        
        # Variables de datos
        self.data = None
        self.similarity_matrix = None
        self.linkage_matrix = None
        self.clusters = None
        self.user_preferences = {}
        self.genre_ontology = self._create_genre_ontology()
        
        self._setup_ui()
        
    def _create_genre_ontology(self):
        """Crear una ontología semántica mejorada de géneros"""
        ontology = {
            'ciencia_ficcion': {'cyberpunk', 'distopia', 'espacial', 'alienigenas', 'tecnologia', 'futuro', 'scifi'},
            'terror': {'paranormal', 'gore', 'slasher', 'psicologico', 'vampiros', 'zombis', 'miedo', 'horror'},
            'aventura': {'epico', 'superheroes', 'road_movie', 'exploracion', 'viaje', 'descubrimiento'},
            'drama': {'biografia', 'psicologico', 'coming_of_age', 'independiente', 'emocional', 'serio'},
            'comedia': {'romantico', 'parodia', 'sketch', 'buddy_movie', 'mockumentary', 'humor', 'risa'},
            'thriller': {'suspenso', 'policiaco', 'espionaje', 'misterio', 'noir', 'tension', 'emocionante'},
            'romance': {'romantico', 'romance_historico', 'amor', 'pasion', 'sentimental'},
            'fantasia': {'medieval', 'mitologia', 'fantasia_urbana', 'epico', 'magia', 'sobrenatural'},
            'animacion': {'infantil', 'familiar', 'animacion_adulta', 'dibujos', 'cartoon'},
            'accion': {'superheroes', 'guerra', 'epico', 'lucha', 'pelea', 'emocion'},
            'documental': {'naturaleza', 'ciencia', 'historia', 'biografia', 'realidad', 'educativo'},
            'historia': {'biografia', 'epico', 'guerra', 'romance_historico', 'historico', 'epoca'},
            'musical': {'familiar', 'romance', 'biografia', 'musica', 'baile', 'cantos'},
            'western': {'epico', 'aventura', 'vaquero', 'frontera', 'oeste'},
            'crimen': {'noir', 'policiaco', 'thriller', 'delito', 'investigacion'},
            'independiente': {'arte', 'experimental', 'festival', 'alternativo'}
        }
        return ontology
    
    def _setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Marco principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Panel de control
        control_frame = ttk.LabelFrame(main_frame, text="Panel de Control", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones
        ttk.Button(control_frame, text="Cargar CSV", 
                  command=self.load_csv).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(control_frame, text="Procesar Datos", 
                  command=self.process_data).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(control_frame, text="Generar Dendrograma", 
                  command=self.create_dendrogram).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(control_frame, text="Matriz Similitud", 
                  command=self.show_similarity_matrix).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(control_frame, text="Ver Ontología", 
                  command=self.show_ontology).grid(row=0, column=4, padx=(0, 5))
        
        # Panel de información
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=8, width=40)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Panel de recomendaciones
        rec_frame = ttk.LabelFrame(main_frame, text="Sistema de Recomendaciones", padding="10")
        rec_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10), padx=(10, 0))
        rec_frame.columnconfigure(1, weight=1)
        
        ttk.Label(rec_frame, text="Seleccionar Usuario:").grid(row=0, column=0, sticky=tk.W)
        self.user_combo = ttk.Combobox(rec_frame, state="readonly")
        self.user_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Button(rec_frame, text="Obtener Recomendaciones", 
                  command=self.get_recommendations).grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        self.rec_text = scrolledtext.ScrolledText(rec_frame, height=6, width=40)
        self.rec_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        rec_frame.rowconfigure(2, weight=1)
        
        # Panel de visualización
        self.viz_frame = ttk.LabelFrame(main_frame, text="Visualizaciones", padding="10")
        self.viz_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.viz_frame.columnconfigure(0, weight=1)
        self.viz_frame.rowconfigure(0, weight=1)
    
    def load_ontology_from_file(self, file_path):
        """Cargar ontología desde archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ontology_data = json.load(f)
                return ontology_data
        except Exception as e:
            print(f"Error al cargar ontología: {e}")
            return self._create_genre_ontology()
    
    def show_ontology(self):
        """Mostrar información de la ontología"""
        ontology_text = "Ontología de Géneros:\n\n"
        for main_genre, related in self.genre_ontology.items():
            ontology_text += f"{main_genre}: {', '.join(related)}\n"
        
        # Crear ventana emergente
        ontology_window = tk.Toplevel(self.root)
        ontology_window.title("Ontología de Géneros")
        ontology_window.geometry("600x400")
        
        text_widget = scrolledtext.ScrolledText(ontology_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, ontology_text)
        text_widget.config(state=tk.DISABLED)
    
    def load_csv(self):
        """Cargar archivo CSV con procesamiento NLP"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Cargar ontología desde archivo si existe
                ontology_path = "C:/Users/ferna/Desktop/jaccardSimilarity/ontology.json"
                try:
                    self.genre_ontology = self.load_ontology_from_file(ontology_path)
                    self.info_text.insert(tk.END, f"✓ Ontología cargada desde {ontology_path}\n")
                except:
                    self.info_text.insert(tk.END, "✓ Usando ontología por defecto\n")
                
                # Leer CSV
                self.data = []
                self.user_preferences = {}
                genres_count = defaultdict(int)
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    csv_reader = csv.reader(file)
                    for row_num, row in enumerate(csv_reader):
                        if row:  # Verificar que la fila no esté vacía
                            user = row[0].strip()
                            processed_genres = set()
                            
                            for genre in row[1:]:
                                if genre.strip():  # Ignorar celdas vacías
                                    # Procesar con NLP
                                    normalized_genre = self.nlp_processor.normalize_genre(genre)
                                    
                                    # Ignorar stop words y palabras muy cortas
                                    if not self.nlp_processor.is_stop_word(normalized_genre):
                                        processed_genres.add(normalized_genre)
                                        genres_count[normalized_genre] += 1
                            
                            self.user_preferences[user] = processed_genres
                            self.data.append([user] + list(processed_genres))
                
                # Actualizar combo de usuarios
                self.user_combo['values'] = list(self.user_preferences.keys())
                
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"✓ CSV cargado exitosamente con procesamiento NLP\n")
                self.info_text.insert(tk.END, f"Usuarios cargados: {len(self.user_preferences)}\n")
                self.info_text.insert(tk.END, f"Géneros únicos después de normalización: {len(genres_count)}\n\n")
                
                # Mostrar estadísticas de géneros
                top_genres = sorted(genres_count.items(), key=lambda x: x[1], reverse=True)[:10]
                self.info_text.insert(tk.END, "Top 10 géneros más populares:\n")
                for genre, count in top_genres:
                    self.info_text.insert(tk.END, f"{genre}: {count} usuarios\n")
                
                # Mostrar muestra de datos procesados
                self.info_text.insert(tk.END, "\nMuestra de datos procesados:\n")
                for i, (user, prefs) in enumerate(list(self.user_preferences.items())[:3]):
                    self.info_text.insert(tk.END, f"{user}: {', '.join(list(prefs)[:5])}\n")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar CSV: {str(e)}")
    
    def _get_all_genres(self):
        """Obtener todos los géneros únicos"""
        all_genres = set()
        for preferences in self.user_preferences.values():
            all_genres.update(preferences)
        return all_genres
    
    def jaccard_similarity(self, set1, set2):
        """Calcular similitud de Jaccard entre dos conjuntos"""
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0
    
    def enhanced_jaccard_similarity(self, set1, set2):
        """Similitud de Jaccard mejorada con ontología semántica y NLP"""
        # Similitud básica de Jaccard
        basic_similarity = self.jaccard_similarity(set1, set2)
        
        # Similitud semántica basada en ontología
        semantic_score = 0
        total_comparisons = 0
        
        for genre1 in set1:
            for genre2 in set2:
                total_comparisons += 1
                if genre1 == genre2:
                    semantic_score += 1
                else:
                    # Verificar relaciones ontológicas
                    related = False
                    # Relaciones directas
                    if (genre1 in self.genre_ontology and 
                        genre2 in self.genre_ontology.get(genre1, set())):
                        semantic_score += 0.8
                        related = True
                    elif (genre2 in self.genre_ontology and 
                          genre1 in self.genre_ontology.get(genre2, set())):
                        semantic_score += 0.8
                        related = True
                    
                    # Relaciones indirectas (mismo grupo ontológico)
                    if not related:
                        for parent, children in self.genre_ontology.items():
                            if genre1 in children and genre2 in children:
                                semantic_score += 0.6
                                break
                        else:
                            # Similitud léxica como último recurso
                            if self.nlp_processor.stemmer.stem(genre1) == self.nlp_processor.stemmer.stem(genre2):
                                semantic_score += 0.4
        
        semantic_similarity = semantic_score / total_comparisons if total_comparisons > 0 else 0
        
        # Combinar similitudes (60% básica, 40% semántica)
        return 0.6 * basic_similarity + 0.4 * semantic_similarity
    
    def process_data(self):
        """Procesar datos y calcular matriz de similitud"""
        if not self.user_preferences:
            messagebox.showwarning("Advertencia", "Primero carga un archivo CSV")
            return
        
        try:
            users = list(self.user_preferences.keys())
            n_users = len(users)
            
            # Crear matriz de similitud
            self.similarity_matrix = np.zeros((n_users, n_users))
            
            for i in range(n_users):
                for j in range(n_users):
                    if i == j:
                        self.similarity_matrix[i][j] = 1.0
                    else:
                        similarity = self.enhanced_jaccard_similarity(
                            self.user_preferences[users[i]], 
                            self.user_preferences[users[j]]
                        )
                        self.similarity_matrix[i][j] = similarity
            
            # Calcular clustering jerárquico
            distance_matrix = 1 - self.similarity_matrix
            np.fill_diagonal(distance_matrix, 0)
            
            condensed_dist = squareform(distance_matrix)
            self.linkage_matrix = linkage(condensed_dist, method='ward')
            
            # Generar clusters
            self.clusters = fcluster(self.linkage_matrix, t=0.7, criterion='distance')
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "✓ Datos procesados exitosamente con NLP\n")
            self.info_text.insert(tk.END, f"Matriz de similitud: {n_users}x{n_users}\n")
            self.info_text.insert(tk.END, f"Clusters identificados: {len(set(self.clusters))}\n\n")
            
            # Mostrar estadísticas de clusters
            cluster_counts = defaultdict(int)
            for cluster in self.clusters:
                cluster_counts[cluster] += 1
            
            self.info_text.insert(tk.END, "Distribución de clusters:\n")
            for cluster, count in sorted(cluster_counts.items()):
                self.info_text.insert(tk.END, f"Cluster {cluster}: {count} usuarios\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar datos: {str(e)}")
    
    def create_dendrogram(self):
        """Crear y mostrar dendrograma"""
        if self.linkage_matrix is None:
            messagebox.showwarning("Advertencia", "Primero procesa los datos")
            return
        
        # Limpiar frame de visualización
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        # Crear figura
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        
        # Crear dendrograma
        users = list(self.user_preferences.keys())
        dendrogram(self.linkage_matrix, labels=users, ax=ax, orientation='top')
        
        ax.set_title('Dendrograma de Clustering Jerárquico de Usuarios', fontsize=14, fontweight='bold')
        ax.set_xlabel('Usuarios', fontsize=12)
        ax.set_ylabel('Distancia', fontsize=12)
        
        # Rotar etiquetas para mejor legibilidad
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Ajustar layout
        fig.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para el canvas
        scrollbar = ttk.Scrollbar(self.viz_frame, orient="horizontal", command=canvas.get_tk_widget().xview)
        scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        canvas.get_tk_widget().configure(xscrollcommand=scrollbar.set)
    
    def show_similarity_matrix(self):
        """Mostrar matriz de similitud como tabla de datos"""
        if self.similarity_matrix is None:
            messagebox.showwarning("Advertencia", "Primero procesa los datos")
            return
        
        # Limpiar frame de visualización
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        # Crear ventana emergente para la tabla
        matrix_window = tk.Toplevel(self.root)
        matrix_window.title("Matriz de Similitud - Vista de Datos")
        matrix_window.geometry("800x600")
        
        # Crear frame principal con scrollbars
        main_frame = ttk.Frame(matrix_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear canvas y scrollbars
        canvas = tk.Canvas(main_frame)
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
        
        # Configurar canvas
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar scrollbars y canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Crear frame interno para la tabla
        table_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=table_frame, anchor="nw")
        
        # Obtener usuarios y datos
        users = list(self.user_preferences.keys())
        n_users = len(users)
        
        # Crear encabezados de columnas
        for j, user in enumerate(users):
            ttk.Label(table_frame, text=user, borderwidth=1, relief="solid", 
                     width=12, background="#f0f0f0", anchor="center").grid(row=0, column=j+1, sticky="nsew")
        
        # Crear filas con datos
        for i, user_row in enumerate(users):
            # Nombre de usuario en la primera columna
            ttk.Label(table_frame, text=user_row, borderwidth=1, relief="solid", 
                     width=12, background="#f0f0f0", anchor="center").grid(row=i+1, column=0, sticky="nsew")
            
            # Valores de similitud
            for j, user_col in enumerate(users):
                similarity = self.similarity_matrix[i][j]
                # Determinar color de fondo basado en el valor de similitud
                color_intensity = int(255 * (1 - similarity))  # Invertido para mejor contraste
                bg_color = f"#{color_intensity:02x}{color_intensity:02x}ff"  # Azul más intenso para mayor similitud
                
                label = ttk.Label(table_frame, text=f"{similarity:.3f}", borderwidth=1, 
                                 relief="solid", width=12, anchor="center")
                label.grid(row=i+1, column=j+1, sticky="nsew")
                
                # Aplicar color de fondo (necesitamos usar tk.Label para bg)
                tk_label = tk.Label(table_frame, text=f"{similarity:.3f}", borderwidth=1, 
                                   relief="solid", width=12, anchor="center", bg=bg_color)
                tk_label.grid(row=i+1, column=j+1, sticky="nsew")
        
        # Configurar grid para expandirse
        for i in range(n_users + 1):
            table_frame.rowconfigure(i, weight=1)
        for j in range(n_users + 1):
            table_frame.columnconfigure(j, weight=1)
        
        # Actualizar scrollregion después de crear los widgets
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        table_frame.bind("<Configure>", configure_scroll_region)
        
        # Añadir leyenda
        legend_frame = ttk.Frame(matrix_window)
        legend_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(legend_frame, text="Leyenda: ").pack(side=tk.LEFT)
        ttk.Label(legend_frame, text="Baja similitud", background="#ffff00").pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="Media similitud", background="#8888ff").pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="Alta similitud", background="#0000ff", foreground="white").pack(side=tk.LEFT, padx=5)
    
    def get_recommendations(self):
        """Obtener recomendaciones para usuario seleccionado"""
        selected_user = self.user_combo.get()
        if not selected_user:
            messagebox.showwarning("Advertencia", "Selecciona un usuario")
            return
        
        if self.similarity_matrix is None:
            messagebox.showwarning("Advertencia", "Primero procesa los datos")
            return
        
        try:
            users = list(self.user_preferences.keys())
            user_idx = users.index(selected_user)
            
            # Obtener similitudes para el usuario seleccionado
            similarities = self.similarity_matrix[user_idx]
            
            # Crear lista de usuarios con sus similitudes (excluyendo al propio usuario)
            user_similarities = []
            for i, similarity in enumerate(similarities):
                if i != user_idx:  # Excluir al propio usuario
                    user_similarities.append((users[i], similarity))
            
            # Ordenar por similitud descendente
            user_similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Mostrar recomendaciones
            self.rec_text.delete(1.0, tk.END)
            self.rec_text.insert(tk.END, f"Recomendaciones para {selected_user}:\n")
            self.rec_text.insert(tk.END, "=" * 40 + "\n\n")
            
            # Mostrar preferencias del usuario seleccionado
            user_prefs = self.user_preferences[selected_user]
            self.rec_text.insert(tk.END, f"Géneros preferidos:\n{', '.join(sorted(user_prefs))}\n\n")
            
            # Top 5 usuarios similares
            self.rec_text.insert(tk.END, "Top 5 usuarios similares:\n")
            for i, (similar_user, similarity) in enumerate(user_similarities[:5]):
                similar_prefs = self.user_preferences[similar_user]
                common_genres = user_prefs.intersection(similar_prefs)
                
                self.rec_text.insert(tk.END, f"\n{i+1}. {similar_user} (Similitud: {similarity:.3f})\n")
                self.rec_text.insert(tk.END, f"   Géneros en común: {', '.join(sorted(common_genres))}\n")
                
                # Géneros únicos del usuario similar que podrían gustar
                unique_genres = similar_prefs - user_prefs
                if unique_genres:
                    self.rec_text.insert(tk.END, f"   Podrían gustarte: {', '.join(sorted(unique_genres))}\n")
            
            # Información del cluster
            if self.clusters is not None:
                user_cluster = self.clusters[user_idx]
                cluster_members = [users[i] for i, cluster in enumerate(self.clusters) if cluster == user_cluster and i != user_idx]
                if cluster_members:
                    self.rec_text.insert(tk.END, f"\nMiembros del mismo cluster ({user_cluster}):\n")
                    self.rec_text.insert(tk.END, ", ".join(cluster_members[:10]))  # Limitar a 10
                    if len(cluster_members) > 10:
                        self.rec_text.insert(tk.END, f" y {len(cluster_members) - 10} más...")
                    self.rec_text.insert(tk.END, "\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar recomendaciones: {str(e)}")


def create_sample_csv():
    """Crear archivo CSV de muestra con variaciones lingüísticas"""
    sample_data = """usuario1,ciencia ficcion,comedia,documental,romance,terror
usuario2,aventura,historia,musical,drama,thriller
usuario3,animacion,accion,fantasia,suspenso,biografia
usuario4,western,crimen,epico,romantico,independiente
usuario5,drama,thriller,accion,ciencia_ficcion,comedia
usuario6,aventura,animacion,superheroes,thriller,catastrofe
usuario7,musical,romance,historia,biografia,familiar
usuario8,scifi,cyberpunk,distopia,accion,suspenso
usuario9,terror,paranormal,gore,thriller,slasher
usuario10,comedia,romantico,buddy movie,parodia,sketch
usuario11,documental,naturaleza,ciencia,historia,biografia
usuario12,fantasia,medieval,epico,aventura,mitologia
usuario13,noir,policiaco,suspenso,investigacion,thriller
usuario14,deportes,competencia,drama,biografia,musical
usuario15,independiente,arte,experimental,festival,drama
usuario16,animacion,infantil,familiar,aventura,comedia
usuario17,ciencia ficcion,espacial,alienigenas,tecnologia,thriller
usuario18,guerra,misterio,road movie,coming of age,zombis
usuario19,vampiros,culto,psicologico,surrealista,animacion adulta
usuario20,mockumentary,romance historico,espionaje,superheroes oscuro,fantasia urbana"""
    
    with open('muestra_usuarios_nlp.csv', 'w', encoding='utf-8') as f:
        f.write(sample_data)
    
    print("Archivo 'muestra_usuarios_nlp.csv' creado exitosamente")

if __name__ == "__main__":
    # Crear archivo de muestra si no existe
    try:
        create_sample_csv()
    except:
        pass
    
    # Ejecutar aplicación
    root = tk.Tk()
    app = UserPreferencesApp(root)
    root.mainloop()