@echo off
echo ========================================
echo   RM4Health Dashboard - Execução
echo ========================================
echo.
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat
echo.
echo Iniciando dashboard...
echo Dashboard estará disponível em: http://127.0.0.1:5000
echo.
echo Para parar o servidor: Ctrl+C
echo.
python app.py
pause
