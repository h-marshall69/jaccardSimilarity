import pandas as pd

class CSVProcessor:
    def __init__(self):
        self.df = None
    
    def load_csv(self, filepath):
        """Cargar el archivo CSV"""
        try:
            self.df = pd.read_csv(filepath)
            return True, None
        except Exception as e:
            return False, f"Error cargando el CSV: {str(e)}"
    
    def get_basic_info(self):
        """Obtener información básica del CSV"""
        if self.df is None:
            return None, "No hay datos cargados"
        
        try:
            info = {
                'total_rows': len(self.df),
                'total_columns': len(self.df.columns),
                'column_names': list(self.df.columns),
                'data_types': self.df.dtypes.astype(str).to_dict(),
                'missing_values': self.df.isnull().sum().to_dict(),
                'sample_data': self.df.head(10).to_dict('records')
            }
            return info, None
            
        except Exception as e:
            return None, f"Error obteniendo información: {str(e)}"
    
    def process_file(self, filepath):
        """Procesar completo del archivo CSV"""
        success, error = self.load_csv(filepath)
        if not success:
            return None, error
        
        info, error = self.get_basic_info()
        if error:
            return None, error
        
        return info, None