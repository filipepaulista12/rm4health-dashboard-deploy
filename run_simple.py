"""Script simples para rodar o dashboard sem debug"""
import os
os.environ['FLASK_DEBUG'] = '0'

from app import app

if __name__ == '__main__':
    print("🚀 Iniciando RM4Health Dashboard (modo produção)...")
    app.run(debug=False, host='0.0.0.0', port=5000)
