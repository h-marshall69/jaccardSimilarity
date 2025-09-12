import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from io import BytesIO
import base64

class VisualizationUtils:
    @staticmethod
    def create_radar_chart(categories, values, title):
        """Crear gráfico radar para visualización de categorías"""
        N = len(categories)
        
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        values += values[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        ax.plot(angles, values, linewidth=2, linestyle='solid')
        ax.fill(angles, values, alpha=0.4)
        
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        plt.xticks(angles[:-1], categories, size=10)
        plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], size=8)
        plt.ylim(0, 1)
        plt.title(title, size=14, y=1.1)
        
        return fig
    
    @staticmethod
    def plot_to_base64(fig):
        """Convertir plot a base64 para HTML"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"