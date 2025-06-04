from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from datetime import date, datetime
import sqlite3
import bcrypt
import pandas as pd
import io
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'
os.makedirs(os.path.join(os.path.dirname(__file__), 'tmp'), exist_ok=True)
DB_NAME = os.path.join(os.path.dirname(__file__), 'tmp', 'salud_adulto.db')

# Crear base de datos si no existe


def crear_base_datos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Crear tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contrasena BLOB NOT NULL,
            rol TEXT NOT NULL
        )
    ''')
    conn.commit()

    # Insertar usuarios predeterminados solo si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        
        admin_pass = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt())
        user_pass = bcrypt.hashpw("abcd".encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                       ("ADMIN", admin_pass, "admin"))
        cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                       ("JUAN", user_pass, "usuario"))
        conn.commit()
        #NOMBRE DEL JEFE DE FAM, NOMBRE DEL PACIENTE , FECHA DE NACIMIENTO Y DOMICILIO 
        #PESO:44KG   TALLA:141CM      T/A:110/80   FC:75X´     FCR:18X´   T:36.6°C      C:-CM    SPO2:%      IMC:22.1
    cursor.execute('''CREATE TABLE IF NOT EXISTS registro_adultos_mayores (
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
        nombre_jefe_fam TEXT,
        paciente TEXT,
        fecha_nacimiento TEXT,
        domicilio TEXT,           
        edad INTEGER,
        sexo TEXT,
        indigena TEXT,
        migrante TEXT,
        nivel_atencion TEXT,
        consulta_enfermeria TEXT,
        consultoria_otorgada TEXT,
        prescripcion_medicamentos TEXT,
        DG_plan_cuidados TEXT,           
        DG_GRUPOS_EDAD TEXT,
        INSTITUCION_PROCEDENCIA TEXT,           
        CONSEJERIA_PF TEXT,
        PF_GRUPOS_EDAD TEXT,           
        PF_SUBSECUENTE TEXT,           
        PF_METODO TEXT,
        VI_EMB_grupo_edad TEXT,           
        VI_EMB_TRIMESTRE_GESTACIONAL TEXT,
        VI_EMB_ACCIONES_IRREDUCTIBLES TEXT,
        observaciones TEXT,           
        DETECCION_TAMIZ TEXT,           
        diagnostico_nutricional TEXT,           
        SALUD_GINECO_DETECCION TEXT,
        EDA_SOBRES_DE_HIDRATACION_ORAL_ENTREGADOS TEXT,
        EDA_MADRES_CAPACITADAS_MANEJO TEXT,           
        IRA_MADRES_CAPACITADAS_MANEJO TEXT,
        grupo_riesgo TEXT,                
        DETECCION_ENFERMEDADES_CRONICAS TEXT,           
        DIABETES_MELLITUS TEXT,           
        DISLIPIDEMIA TEXT,           
        hipertension TEXT,       
        REVISION_INTEGRAL_PIEL_MIEMBROS_INFERIORES TEXT,
        DIABETICOS_INFORMADOS_CUIDADOS_PIES TEXT,
        vacunacion TEXT,           
        PROMOCION_SALUD,
        DERIVACION TEXT,           
        ACTIVIDADES_ASISTENCIALES TEXT,
        OBSERVACIONES_GENERALES TEXT
           
    )''')
    conn.commit()

    conn.close()

@app.route('/')
def home():
    #if current_user.is_authenticated:
    #    return redirect(url_for('dashboard'))  # o la vista principal para usuarios logueados
    #else:
    #   return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT contrasena, rol FROM usuarios WHERE usuario = ?", (usuario.upper(),))
        registro = cursor.fetchone()
        conn.close()

        # Convertir la contraseña almacenada (str) a bytes antes de usar bcrypt.checkpw
        if registro and bcrypt.checkpw(contrasena.encode('utf-8'), registro[0]):
        #if registro and bcrypt.checkpw(contrasena.encode('utf-8'), registro[0].encode('utf-8')):
            session['usuario'] = usuario
            session['rol'] = registro[1]
            flash('Inicio de sesión exitoso', 'info')
            return redirect(url_for('formulario'))
        else:
            flash('Credenciales incorrectas', 'error')
            return redirect(url_for('login'))

    # GET request
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        usuario = request.form['usuario'].upper()
        contrasena = request.form['contrasena']
        rol = request.form['rol']  # Por ejemplo: 'admin', 'enfermero', etc.

        # Hashear la contraseña
       
        #hashed = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
        hashed_str = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
        #hashed_str = hashed.decode('utf-8')

        # Conexión a la base de datos
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Verificar si el usuario ya existe
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (usuario,))
        if cursor.fetchone():
            conn.close()
            flash('El usuario ya existe.', 'warning')
            return redirect(url_for('registro'))

        # Insertar nuevo usuario
        cursor.execute("INSERT INTO usuarios (usuario, contrasena, rol) VALUES (?, ?, ?)",
                       (usuario, hashed_str, rol))
        conn.commit()
        conn.close()

        flash('Usuario registrado correctamente', 'success')
        return redirect(url_for('login'))
    # Si es GET, mostrar el formulario
    return render_template('registrar_usuario.html')
from datetime import datetime

def campos_validos(form):
    # Lista de campos obligatorios
    campos_obligatorios = [
        'unidad_salud', 'entidad_federativa', 'clues', 'localidad', 'servicio',
        'personal_enfermeria', 'fecha', 'hora_inicio', 'hora_termino', 'nombre_jefe_fam',
        'paciente', 'fecha_nacimiento', 'domicilio', 'edad', 'sexo', 'indigena',
        'migrante', 'nivel_atencion', 'consulta_enfermeria', 'consultoria_otorgada',
        'prescripcion_medicamentos', 'DG_plan_cuidados', 'DG_GRUPOS_EDAD',
        'INSTITUCION_PROCEDENCIA', 'CONSEJERIA_PF', 'PF_GRUPOS_EDAD', 'PF_SUBSECUENTE',
        'PF_METODO', 'VI_EMB_grupo_edad', 'VI_EMB_TRIMESTRE_GESTACIONAL',
        'VI_EMB_ACCIONES_IRREDUCTIBLES', 'observaciones', 'DETECCION_TAMIZ',
        'diagnostico_nutricional', 'SALUD_GINECO_DETECCION',
        'EDA_SOBRES_DE_HIDRATACION_ORAL_ENTREGADOS',
        'EDA_MADRES_CAPACITADAS_MANEJO', 'IRA_MADRES_CAPACITADAS_MANEJO',
        'grupo_riesgo', 'DETECCION_ENFERMEDADES_CRONICAS', 'DIABETES_MELLITUS',
        'DISLIPIDEMIA', 'hipertension', 'REVISION_INTEGRAL_PIEL_MIEMBROS_INFERIORES',
        'DIABETICOS_INFORMADOS_CUIDADOS_PIES', 'vacunacion', 'PROMOCION_SALUD',
        'DERIVACION', 'ACTIVIDADES_ASISTENCIALES', 'OBSERVACIONES_GENERALES'
    ]

    # Validar que todos estén presentes y no vacíos
    for campo in campos_obligatorios:
        valor = form.get(campo, '').strip()
        if valor == '':
            return False, campo

    # Validar edad
    edad_str = form.get('edad', '').strip()
    try:
        edad = int(edad_str)
        if edad <= 0:
            return False, 'edad (valor no válido)'
    except ValueError:
        return False, 'edad (no numérico)'

    # Validar fecha
    fecha_str = form.get('fecha', '').strip()
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        if fecha > datetime.now():
            return False, 'fecha (futura)'
    except ValueError:
        return False, 'fecha (formato inválido)'

    # Validar horas
    hora_inicio_str = form.get('hora_inicio', '').strip()
    hora_termino_str = form.get('hora_termino', '').strip()
    try:
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M')
        hora_termino = datetime.strptime(hora_termino_str, '%H:%M')
        if hora_inicio >= hora_termino:
            return False, 'hora_inicio (debe ser anterior a hora_termino)'
    except ValueError:
        return False, 'hora_inicio o hora_termino (formato inválido)'

    return True, None

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if 'usuario' not in session:
        flash('Debes iniciar sesión', 'error')
        return redirect(url_for('login'))

    if session['rol'] == 'admin':
        return render_template('admin.html', usuario=session['usuario'])
    if request.method == 'POST':
        validado, campo_faltante = campos_validos(request.form)
        if not validado:
            flash(f'Por favor completa el campo: {campo_faltante.replace("_", " ").capitalize()}', 'danger')
            return redirect('/')

        try:
            data = (
                request.form.get('unidad_salud', ''),
                request.form.get('entidad_federativa', ''),
                request.form.get('clues', ''),
                request.form.get('localidad', ''),
                request.form.get('servicio', ''),
                request.form.get('personal_enfermeria', ''),
                request.form.get('fecha', ''),
                request.form.get('hora_inicio', ''),
                request.form.get('hora_termino', ''),
                request.form.get('nombre_jefe_fam', ''),
                request.form.get('paciente', ''),
                request.form.get('fecha_nacimiento', ''),
                request.form.get('domicilio', ''),
                int(request.form.get('edad', 0)),  # 0 por defecto; valida antes que sea > 0
                request.form.get('sexo', ''),
                request.form.get('indigena', ''),
                request.form.get('migrante', ''),
                request.form.get('nivel_atencion', ''),
                request.form.get('consulta_enfermeria', ''),
                request.form.get('consultoria_otorgada', ''),
                request.form.get('prescripcion_medicamentos', ''),
                request.form.get('DG_plan_cuidados', ''),
                request.form.get('DG_GRUPOS_EDAD', ''),
                request.form.get('INSTITUCION_PROCEDENCIA', ''),
                request.form.get('CONSEJERIA_PF', ''),
                request.form.get('PF_GRUPOS_EDAD', ''),
                request.form.get('PF_SUBSECUENTE', ''),
                request.form.get('PF_METODO', ''),
                request.form.get('VI_EMB_grupo_edad', ''),
                request.form.get('VI_EMB_TRIMESTRE_GESTACIONAL', ''),
                request.form.get('VI_EMB_ACCIONES_IRREDUCTIBLES', ''),
                request.form.get('observaciones',''),
                request.form.get('DETECCION_TAMIZ', ''),
                request.form.get('diagnostico_nutricional', ''),
                request.form.get('SALUD_GINECO_DETECCION', ''),
                request.form.get('EDA_SOBRES_DE_HIDRATACION_ORAL_ENTREGADOS', ''),
                request.form.get('EDA_MADRES_CAPACITADAS_MANEJO', ''),
                request.form.get('IRA_MADRES_CAPACITADAS_MANEJO', ''),
                request.form.get('grupo_riesgo', ''),
                request.form.get('DETECCION_ENFERMEDADES_CRONICAS', ''),
                request.form.get('DIABETES_MELLITUS', ''),
                request.form.get('DISLIPIDEMIA', ''),
                request.form.get('hipertension', ''),
                request.form.get('REVISION_INTEGRAL_PIEL_MIEMBROS_INFERIORES', ''),
                request.form.get('DIABETICOS_INFORMADOS_CUIDADOS_PIES', ''),
                request.form.get('vacunacion', ''),
                request.form.get('PROMOCION_SALUD', ''),
                request.form.get('DERIVACION', ''),
                request.form.get('ACTIVIDADES_ASISTENCIALES', ''),
                request.form.get('OBSERVACIONES_GENERALES', '')
            )

            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute('''INSERT INTO registro_adultos_mayores (
                unidad_salud,
                entidad_federativa,
                clues,
                localidad,
                servicio,
                personal_enfermeria, 
                fecha,
                hora_inicio, 
                hora_termino,
                nombre_jefe_fam, 
                paciente,
                fecha_nacimiento, 
                domicilio,    
                edad,
                sexo,
                indigena,
                migrante,
                nivel_atencion,
                consulta_enfermeria,
                consultoria_otorgada,
                prescripcion_medicamentos, 
                DG_plan_cuidados, 
                DG_GRUPOS_EDAD,
                INSTITUCION_PROCEDENCIA,           
                CONSEJERIA_PF,
                PF_GRUPOS_EDAD,           
                PF_SUBSECUENTE,          
                PF_METODO,
                VI_EMB_grupo_edad,
                VI_EMB_TRIMESTRE_GESTACIONAL,
                VI_EMB_ACCIONES_IRREDUCTIBLES,
                observaciones,           
                DETECCION_TAMIZ,          
                diagnostico_nutricional,           
                SALUD_GINECO_DETECCION, 
                EDA_SOBRES_DE_HIDRATACION_ORAL_ENTREGADOS,
                EDA_MADRES_CAPACITADAS_MANEJO,
                IRA_MADRES_CAPACITADAS_MANEJO,
                grupo_riesgo,               
                DETECCION_ENFERMEDADES_CRONICAS,           
                DIABETES_MELLITUS,           
                DISLIPIDEMIA,            
                hipertension,       
                REVISION_INTEGRAL_PIEL_MIEMBROS_INFERIORES,
                DIABETICOS_INFORMADOS_CUIDADOS_PIES,
                vacunacion,           
                PROMOCION_SALUD,
                DERIVACION,           
                ACTIVIDADES_ASISTENCIALES,
                OBSERVACIONES_GENERALES
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
            print(len(data))                
            conn.commit()
            conn.close()
            flash('Registro guardado exitosamente.', 'success')
        except Exception as e:
            flash(f'Error al guardar: {e}', 'danger')
        return redirect(url_for('formulario'))
        #return redirect('/')
    usua = session['usuario']
    hoy = date.today().isoformat()  # formato YYYY-MM-DD
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT * FROM registro_adultos_mayores
        WHERE personal_enfermeria = ? AND fecha = ?
    """, (usua, hoy))
    registros = c.fetchall()
    conn.close()

    return render_template('formulario.html', registros=registros)
@app.route('/eliminar/<int:registro_id>', methods=['POST'])
def eliminar(registro_id):
    conn = sqlite3.connect('salud_adulto.db')
    c = conn.cursor()
    c.execute('DELETE FROM registro_adultos_mayores WHERE id = ?', (registro_id,))
    conn.commit()
    conn.close()
    flash('Registro eliminado.', 'info')
    return redirect('/')
@app.route('/exportar', methods=['GET'])
def exportar():
    fecha_inicio = request.args.get('fecha_inicio')  # antes: request.form.get
    fecha_fin = request.args.get('fecha_fin')        # antes: request.form.get

    if not fecha_inicio or not fecha_fin:
        flash("Debes seleccionar un rango de fechas.", "warning")
        return redirect('/formulario')  # o la ruta donde esté el formulario

    try:
        # Conexión a la base de datos
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query('SELECT * FROM registro_adultos_mayores', conn)
        conn.close()

        # Asegurar tipo datetime en la columna 'fecha'
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

        # Filtrar por el rango de fechas
        df = df[(df['fecha'] >= fecha_inicio) & (df['fecha'] <= fecha_fin)]

        # Agregar columnas día, mes, año
        fecha_index = df.columns.get_loc('fecha')
        df.insert(fecha_index, 'día', df['fecha'].dt.day)
        df.insert(fecha_index + 1, 'mes', df['fecha'].dt.month)
        df.insert(fecha_index + 2, 'año', df['fecha'].dt.year)

        # Concatenar jefe de familia + paciente + fecha + domicilio
        df['jefe_de_familia'] = (
            "Jf: " + df['nombre_jefe_fam'].fillna('') + " | " +
            "Pte: " + df['paciente'].fillna('') + " | " +
            "Fn: " + df['fecha_nacimiento'].fillna('') + " | " +
            "Dom: " + df['domicilio'].fillna('')
        )

        jefe_index = df.columns.get_loc('nombre_jefe_fam')
        df.insert(jefe_index,
                  'NOMBRE DEL JEFE DE FAM, NOMBRE DEL PACIENTE , FECHA DE NACIMIENTO Y DOMICILIO',
                  df['jefe_de_familia'])

        # Eliminar columnas no deseadas
        df.drop(columns=[
            'id', 'nombre_jefe_fam', 'paciente',
            'fecha_nacimiento', 'domicilio', 'fecha', 'jefe_de_familia'
        ], inplace=True)

        # Exportar a Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Registros', index=False)
        output.seek(0)

        nombre_archivo = f"registros_{fecha_inicio}_a_{fecha_fin}.xlsx"
        return send_file(output, download_name=nombre_archivo, as_attachment=True)

    except Exception as e:
        flash(f"Error al exportar: {str(e)}", "danger")
        return redirect('/formulario')

if __name__ == '__main__':
    crear_base_datos()
    app.run(debug=True)

    #app.run(host="0.0.0.0", port=5000, debug=True)

