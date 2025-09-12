import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-segura'

    # Data
    DATA_FOLDER = os.path.join(basedir, 'app', 'data')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    ALLOWED_EXTENSIONS = {'csv'}
    
    # Crear directorio de uploads si no existe
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)