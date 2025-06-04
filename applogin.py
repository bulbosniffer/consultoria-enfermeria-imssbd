from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import sqlite3
import pandas as pd
import io
import bcrypt
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

DB_NAME = os.path.join(os.path.dirname(__file__), 'salud_adulto.db')

# ----------- Base de datos y usuarios -----------
def crear_base_datos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')

    # Tabla de registros clínicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_adultos_mayores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unidad_salud TEXT,
            entidad_federativa TEXT,
            clues TEXT,
            localidad TEXT,
            servicio TEXT,
            personal_enfermeria TEXT,
            fecha TEXT,
            hora_inicio TEXT,
            hora_termino TEXT,
            paciente TEXT,
            edad INTEGER,
            sexo TEXT,
            indigena TEXT,
            migrante TEXT,
            grupo_edad TEXT,
            nivel_atencion TEXT,
            consulta_enfermeria TEXT,
            plan_cuidados TEXT,
            diabetes TEXT,
            hipertension TEXT,
            vacunacion TEXT,
            observaciones TEXT,
            nombre_jefe_fam TEXT,
            fecha_nacimiento TEXT,
            domicilio TEXT,
            consultoria_otorgada TEXT,
            prescripcion_medicamentos TEXT,
            diagnostico_nutricional TEXT,
            grupo_riesgo TEXT
        )
    ''')
    conn.commit()

    # Insertar usuarios iniciales si no existen
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        admin_pass = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_pass = bcrypt.hashpw("abcd".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)", ("admin", admin_pass, "admin"))
        cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)", ("juan", user_pass, "usuario"))
        conn.commit()

    conn.close()

# ----------- Validación de formulario -----------
def campos_validos(form):
    for campo in form:
        if form[campo].strip() == '':
            return False, campo
    try:
        edad = int(form['edad'])
        if edad <= 0:
            return False, 'edad'
    except ValueError:
        return False, 'edad'
    try:
        fecha = datetime.strptime(form['fecha'], '%Y-%m-%d')
        if fecha > datetime.now():
            return False, 'fecha'
    except ValueError:
        return False, 'fecha'
    try:
        inicio = datetime.strptime(form['hora_inicio'], '%H:%M')
        fin = datetime.strptime(form['hora_termino'], '%H:%M')
        if inicio >= fin:
            return False, 'hora_inicio'
    except ValueError:
        return False, 'hora_inicio'
    return True, None

# ----------- Rutas principales -----------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT contrasena, rol FROM usuarios WHERE usuario = ?", (usuario,))
        registro = cursor.fetchone()
        conn.close()

        if registro and bcrypt.checkpw(contrasena.encode('utf-8'), registro[0].encode('utf-8')):
            session['usuario'] = usuario
            session['rol'] = registro[1]
            flash('Inicio de sesión exitoso', 'info')
            return redirect(url_for('formulario'))
        else:
            flash('Credenciales incorrectas', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        rol = request.form['rol']
        hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
        if cursor.fetchone():
            conn.close()
            flash('El usuario ya existe.', 'warning')
            return redirect(url_for('registrar_usuario'))
        cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)", (usuario, hashed, rol))
        conn.commit()
        conn.close()
        flash('Usuario registrado correctamente', 'success')
        return redirect(url_for('login'))
    return render_template('registrar_usuario.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if 'usuario' not in session:
        flash('Debes iniciar sesión.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        valido, campo = campos_validos(request.form)
        if not valido:
            flash(f'Completa el campo: {campo}', 'danger')
            return redirect(url_for('formulario'))

        try:
            data = tuple(request.form.get(campo) for campo in [
                'unidad_salud', 'entidad_federativa', 'clues', 'localidad', 'servicio',
                'personal_enfermeria', 'fecha', 'hora_inicio', 'hora_termino', 'paciente',
                'edad', 'sexo', 'indigena', 'migrante', 'grupo_edad', 'nivel_atencion',
                'consulta_enfermeria', 'plan_cuidados', 'diabetes', 'hipertension',
                'vacunacion', 'observaciones', 'nombre_jefe_fam', 'fecha_nacimiento',
                'domicilio', 'consultoria_otorgada', 'prescripcion_medicamentos',
                'diagnostico_nutricional', 'grupo_riesgo'
            ])
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('''INSERT INTO registro_adultos_mayores (
                unidad_salud, entidad_federativa, clues, localidad, servicio,
                personal_enfermeria, fecha, hora_inicio, hora_termino, paciente,
                edad, sexo, indigena, migrante, grupo_edad,
                nivel_atencion, consulta_enfermeria, plan_cuidados,
                diabetes, hipertension, vacunacion, observaciones,
                nombre_jefe_fam, fecha_nacimiento, domicilio,
                consultoria_otorgada, prescripcion_medicamentos,
                diagnostico_nutricional, grupo_riesgo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
            conn.commit()
            conn.close()
            flash('Registro guardado exitosamente.', 'success')
        except Exception as e:
            flash(f'Error al guardar: {e}', 'danger')
        return redirect(url_for('formulario'))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM registro_adultos_mayores')
    registros = c.fetchall()
    conn.close()
    return render_template('formulario.html', registros=registros, usuario=session['usuario'])

@app.route('/eliminar/<int:registro_id>', methods=['POST'])
def eliminar(registro_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM registro_adultos_mayores WHERE id = ?', (registro_id,))
    conn.commit()
    conn.close()
    flash('Registro eliminado.', 'info')
    return redirect(url_for('formulario'))

@app.route('/exportar')
def exportar():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query('SELECT * FROM registro_adultos_mayores', conn)
    conn.close()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Registros', index=False)
    output.seek(0)
    return send_file(output, download_name="registros_salud_adulto.xlsx", as_attachment=True)

# ----------- Main -----------
if __name__ == '__main__':
    crear_base_datos()
    app.run(host="0.0.0.0", port=5000, debug=True)

