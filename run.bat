@echo off
echo ============================================================
echo   Pole Guy Wire Calculator - Web Application
echo   95 sq.mm Steel Strand ^& 3 Conductor Levels System
echo ============================================================
echo.

python -c "import flask" 2>NUL
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
)

echo Starting Flask server on http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
python app.py
pause
