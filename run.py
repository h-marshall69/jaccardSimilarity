from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Obtener puerto de variable de entorno o usar 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)