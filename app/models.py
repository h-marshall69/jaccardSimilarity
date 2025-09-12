import pandas as pd
import os
from datetime import datetime

class CSVFile:
    def __init__(self, filename, filepath):
        self.filename = filename
        self.filepath = filepath
        self.upload_date = datetime.now()
        self.data = None
    
    def load_data(self):
        """Cargar datos del CSV usando pandas"""
        try:
            self.data = pd.read_csv(self.filepath)
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def get_info(self):
        """Obtener información básica del CSV"""
        if self.data is not None:
            return {
                'filename': self.filename,
                'rows': len(self.data),
                'columns': list(self.data.columns),
                'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S')
            }
        return None