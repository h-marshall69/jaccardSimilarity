from flask import Flask
from .config import Config
from .routes.main import main_bp
from .errors.handlers import errors_bp

def create_app(config_class=Config):
    """
    Application Factory Pattern
    """
    app = Flask(__name__)

    # Configuración
    app.config.from_object(config_class)
    
    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(errors_bp)
    
    return app