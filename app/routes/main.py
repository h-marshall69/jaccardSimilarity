from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.file_service import FileService
from app.utils.csv_processor import CSVProcessor

main_bp = Blueprint('main', __name__)

# Inicializar servicios
file_service = FileService()
csv_processor = CSVProcessor()

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
        
        info, error = csv_processor.process_file(file_info['filepath'])
        
        if error:
            flash(error)
            file_service.delete_file(file_info['filepath'])
            return redirect(request.url)
        
        flash('Archivo subido y procesado correctamente!')
        return render_template('results.html', info=info, filename=file_info['filename'])
    
    return render_template('index.html')