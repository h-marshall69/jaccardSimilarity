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
warnings.filterwarnings('ignore')

class UserPreferencesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Análisis de Preferencias de Usuarios")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables de datos
        self.data = None
        self.similarity_matrix = None
        self.linkage_matrix = None
        self.clusters = None
        self.user_preferences = {}
        self.genre_ontology = self._create_genre_ontology()
        
        self._setup_ui()
        
    def _create_genre_ontology(self):
        """Crear una ontología semántica básica de géneros"""
        ontology = {
            'ciencia_ficcion': {'cyberpunk', 'distopía', 'espacial', 'alienígenas', 'tecnología'},
            'terror': {'paranormal', 'gore', 'slasher', 'psicológico', 'vampiros'},
            'aventura': {'épico', 'superhéroes', 'road_movie', 'espacial'},
            'drama': {'biografía', 'psicológico', 'coming_of_age', 'independiente'},
            'comedia': {'romántico', 'parodia', 'sketch', 'buddy_movie', 'mockumentary'},
            'thriller': {'suspenso', 'policíaco', 'espionaje', 'misterio', 'noir'},
            'romance': {'romántico', 'romance_histórico'},
            'fantasía': {'medieval', 'mitología', 'fantasía_urbana', 'épico'},
            'animación': {'infantil', 'familiar', 'animación_adulta'},
            'acción': {'superhéroes', 'guerra', 'épico'},
            'documental': {'naturaleza', 'ciencia', 'historia', 'biografía'},
            'historia': {'biografía', 'épico', 'guerra', 'romance_histórico'},
            'musical': {'familiar', 'romance', 'biografía'},
            'western': {'épico', 'aventura'},
            'crimen': {'noir', 'policíaco', 'thriller'},
            'independiente': {'arte', 'experimental', 'festival'}
        }
        return ontology
    
    def _setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
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
        
    def load_csv(self):
        """Cargar archivo CSV"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Leer CSV con el formato específico
                self.data = []
                self.user_preferences = {}
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    csv_reader = csv.reader(file)
                    for row in csv_reader:
                        if row:  # Verificar que la fila no esté vacía
                            user = row[0]
                            preferences = set(row[1:])  # Convertir a conjunto
                            self.user_preferences[user] = preferences
                            self.data.append([user] + list(preferences))
                
                # Actualizar combo de usuarios
                self.user_combo['values'] = list(self.user_preferences.keys())
                
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"✓ CSV cargado exitosamente\n")
                self.info_text.insert(tk.END, f"Usuarios cargados: {len(self.user_preferences)}\n")
                self.info_text.insert(tk.END, f"Géneros únicos: {len(self._get_all_genres())}\n\n")
                
                # Mostrar muestra de datos
                self.info_text.insert(tk.END, "Muestra de datos:\n")
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
        """Similitud de Jaccard mejorada con ontología semántica"""
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
                    if (genre1 in self.genre_ontology and 
                        genre2 in self.genre_ontology.get(genre1, set())):
                        semantic_score += 0.7
                    elif (genre2 in self.genre_ontology and 
                          genre1 in self.genre_ontology.get(genre2, set())):
                        semantic_score += 0.7
                    else:
                        # Buscar relaciones indirectas
                        for parent, children in self.genre_ontology.items():
                            if genre1 in children and genre2 in children:
                                semantic_score += 0.5
                                break
        
        semantic_similarity = semantic_score / total_comparisons if total_comparisons > 0 else 0
        
        # Combinar similitudes (70% básica, 30% semántica)
        return 0.7 * basic_similarity + 0.3 * semantic_similarity
    
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
            # Convertir similitud a distancia
            distance_matrix = 1 - self.similarity_matrix
            np.fill_diagonal(distance_matrix, 0)  # Diagonal en 0
            
            # Convertir a formato condensado para scipy
            condensed_dist = squareform(distance_matrix)
            self.linkage_matrix = linkage(condensed_dist, method='ward')
            
            # Generar clusters
            self.clusters = fcluster(self.linkage_matrix, t=0.7, criterion='distance')
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "✓ Datos procesados exitosamente\n")
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
        """Mostrar matriz de similitud como heatmap"""
        if self.similarity_matrix is None:
            messagebox.showwarning("Advertencia", "Primero procesa los datos")
            return
        
        # Limpiar frame de visualización
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        # Crear figura
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        
        # Crear heatmap
        users = list(self.user_preferences.keys())
        sns.heatmap(self.similarity_matrix, 
                   xticklabels=users, 
                   yticklabels=users,
                   annot=False, 
                   cmap='viridis',
                   square=True,
                   ax=ax)
        
        ax.set_title('Matriz de Similitud entre Usuarios', fontsize=14, fontweight='bold')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        plt.setp(ax.get_yticklabels(), rotation=0)
        
        fig.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
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
    """Crear archivo CSV de muestra"""
    sample_data = """usuario1,ciencia_ficcion,comedia,documental,romance,terror
usuario2,aventura,historia,musical,drama,thriller
usuario3,animación,acción,fantasía,suspenso,biografía
usuario4,western,crimen,épico,romántico,independiente
usuario5,drama,thriller,acción,ciencia_ficcion,comedia
usuario6,aventura,animación,superhéroes,thriller,catástrofe
usuario7,musical,romance,historia,biografía,familiar
usuario8,ciencia_ficcion,cyberpunk,distopía,acción,suspenso
usuario9,terror,paranormal,gore,thriller,slasher
usuario10,comedia,romántico,buddy_movie,parodia,sketch
usuario11,documental,naturaleza,ciencia,historia,biografía
usuario12,fantasía,medieval,épico,aventura,mitología
usuario13,noir,policíaco,suspenso,investigación,thriller
usuario14,deportes,competencia,drama,biografía,musical
usuario15,independiente,arte,experimental,festival,drama
usuario16,animación,infantil,familiar,aventura,comedia
usuario17,ciencia_ficcion,espacial,alienígenas,tecnología,thriller
usuario18,guerra,misterio,road_movie,coming_of_age,zombis
usuario19,vampiros,culto,psicológico,surrealista,animación_adulta
usuario20,mockumentary,romance_histórico,espionaje,superheroes_oscuro,fantasía_urbana"""
    
    with open('muestra_usuarios.csv', 'w', encoding='utf-8') as f:
        f.write(sample_data)
    
    print("Archivo 'muestra_usuarios.csv' creado exitosamente")

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