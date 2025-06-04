@echo off
setlocal

REM Crear entorno virtual si no existe
IF NOT EXIST venv (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar si Flask está instalado
pip show flask >nul 2>&1
IF ERRORLEVEL 1 (
    echo Flask no está instalado. Instalando Flask...
    pip install flask
)

REM Configurar variables de entorno para Flask
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_RUN_HOST=192.168.100.100
set FLASK_RUN_PORT=5000

REM Abrir navegador automáticamente
start http://192.168.100.100:5000

REM Iniciar el servidor Flask y guardar log
echo Iniciando servidor Flask...
flask run > flask_log.txt 2>&1

endlocal
pause
