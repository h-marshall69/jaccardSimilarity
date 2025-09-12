import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app

class FileService:
    def __init__(self):
        pass  # La configuración se obtiene de current_app cuando se usa
    
    def is_allowed_file(self, filename):
        """Verificar si la extensión del archivo es permitida"""
        if not filename:
            return False
            
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    def save_file(self, file):
        """Guardar el archivo de manera segura"""
        if not file or file.filename == '':
            return None, "No se seleccionó ningún archivo"
        
        if not self.is_allowed_file(file.filename):
            return None, "Solo se permiten archivos CSV"
        
        filename = secure_filename(file.filename)
        data_folder = current_app.config['DATA_FOLDER']
        filepath = os.path.join(data_folder, filename)
        
        try:
            # Evitar sobreescribir archivos existentes
            counter = 1
            original_filename = filename
            while os.path.exists(filepath):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                filepath = os.path.join(data_folder, filename)
                counter += 1
            
            file.save(filepath)
            return {
                'filename': filename,
                'filepath': filepath,
                'upload_date': datetime.now()
            }, None
            
        except Exception as e:
            return None, f"Error al guardar el archivo: {str(e)}"
    
    def delete_file(self, filepath):
        """Eliminar archivo"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True, None
            return False, "El archivo no existe"
        except Exception as e:
            return False, f"Error al eliminar el archivo: {str(e)}"