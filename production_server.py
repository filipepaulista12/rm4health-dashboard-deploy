#!/usr/bin/env python3
"""
Servidor de produção usando Waitress (Windows/Linux compatível)
"""
from waitress import serve
import os

# Definir que estamos em produção
os.environ['PRODUCTION'] = '1'

from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Iniciando servidor de produção...")
    print(f"📍 Host: {host}")  
    print(f"🔌 Porta: {port}")
    print(f"🌐 URL: http://{host}:{port}")
    
    serve(app, host=host, port=port, threads=4)
