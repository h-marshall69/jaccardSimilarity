from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL

app=Flask(__name__)

# Conexion MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'abaco'

conexion = MySQL(app)

@app.before_request
def before_request():
    print('Antes de la peticion ...')

@app.after_request
def after_request(response):
    print('Despues de la peticon')
    
    return response

@app.route('/')
def index():
    #return "<h1>Hola mundo</h1>"

    return render_template('index.html')

@app.route('/contacto/<nombre>/<int:edad>')
def contacto(nombre, edad):
    data={
        'titulo': 'contacto',
        'nombre': nombre,
        'edad': edad
    }

    return render_template('contacto.html', data=data)


def query_string():
    print(request)
    
    return 'Ok'

@app.route('/cursos')
def listar_cursos():
    data = []
    try:
        cursor = conexion.connection.cursot()
        sql = "SELEC codigo, nombre, creditos FROM curso ORDER BY nombre ASC"
        cursor.execute(sql)
        cursos = cursor.fetchall()
        data['cursos'] = cursos
        data['mensaje'] = 'Exito'
    except Exception as ex:
        data['mensaje'] = 'Error...'
    return jsonify(data)

def pagina_no_encontrada(error):
    #return render_template('404.html'), 404
    return redirect(url_for('index'))

if __name__=='__main__':
    app.add_url_rule('/query_string', view_func=query_string)
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True, port=5000)  