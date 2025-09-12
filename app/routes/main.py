from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
import os
from werkzeug.utils import secure_filename

# Importar servicios
from app.services.file_service import FileService
from app.services.similarity_service import SimilarityService

main_bp = Blueprint('main', __name__)

# Inicializar servicios
file_service = FileService()
similarity_service = SimilarityService()

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo')
            return redirect(request.url)
        
        file = request.files['file']
        file_info, error = file_service.save_file(file)
        
        if error:
            flash(error)
            return redirect(request.url)


        # Procesar el dataset con similitud
        results, error = similarity_service.process_dataset(file_info['filepath'])
        
        if error:
            flash(error)
            file_service.delete_file(file_info['filepath'])
            return redirect(request.url)
        
        flash('Dataset procesado correctamente!')
        return render_template('results.html', results=results, filename=file_info['filename'])
    
    return render_template('index.html')