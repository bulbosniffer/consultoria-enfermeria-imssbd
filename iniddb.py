import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
	drop table registro_adultos_mayores
''')
conn.commit()
print("Base de datos borrada.")

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
        nombre_jefe_fam TEXT,
        paciente TEXT,
        fecha_nacimiento TEXT,
        domicilio TEXT,           
        edad TEXT,
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
           
    )
''')

conn.commit()
conn.close()
print("Base de datos creada.")