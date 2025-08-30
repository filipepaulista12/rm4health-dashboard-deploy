@echo off
echo ================================================
echo    Deploy RM4Health Dashboard - Render.com
echo ================================================
echo.

echo [1/4] Commitando alteracoes...
git add .
git commit -m "feat: Preparacao para deploy online - dados locais"

echo.
echo [2/4] Enviando para GitHub...  
git push origin deploy-online-compartilhado

echo.
echo [3/4] Instrucoes para Render.com:
echo.
echo 1. Acesse https://render.com
echo 2. Conecte seu repositorio GitHub
echo 3. Configure:
echo    - Build Command: pip install -r requirements_production.txt
echo    - Start Command: python production_server.py
echo    - Branch: deploy-online-compartilhado
echo.
echo [4/4] URLs dos dados locais:
dir redcap_data_*.json
echo.
echo ✅ Deploy preparado!
pause
