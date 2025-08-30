@echo off
echo ================================================
echo    RM4Health Dashboard - Atualizacao de Dados
echo ================================================
echo.

echo [1/3] Ativando ambiente virtual...
call C:\Users\up739088\Desktop\FMUP\rm4isep\.venv\Scripts\activate.bat

echo.
echo [2/3] Extraindo dados do REDCap...
python extract_data.py

echo.
echo [3/3] Dados atualizados com sucesso!
echo.
echo Para iniciar o dashboard:
echo    python app.py
echo.
echo URL: http://127.0.0.1:5000
echo.
pause
