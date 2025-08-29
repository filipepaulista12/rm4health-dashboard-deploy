@echo off
echo ======================================
echo    RM4Health Dashboard Local Setup
echo ======================================

echo.
echo [1/3] Instalando Streamlit...
pip install streamlit plotly

echo.
echo [2/3] Testando conexao com REDCap...
python -c "from redcap_client import REDCapClient; print('✅ REDCap client OK')" 2>nul || echo "⚠️ REDCap client com problemas - mas dashboard vai funcionar com dados locais"

echo.
echo [3/3] Iniciando dashboard...
echo.
echo ========================================
echo    Dashboard iniciando em http://localhost:8501
echo    Pressione Ctrl+C para parar
echo ========================================
echo.

streamlit run dashboard_local.py --server.port 8501 --server.headless false
