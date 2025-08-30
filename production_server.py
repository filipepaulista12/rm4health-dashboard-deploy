#!/usr/bin/env python3
"""
Servidor de produção usando Waitress (Windows/Linux compatível)
"""
from waitress import serve
from app import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Iniciando servidor de produção...")
    print(f"📍 Host: {host}")  
    print(f"🔌 Porta: {port}")
    print(f"🌐 URL: http://{host}:{port}")
    
    serve(app, host=host, port=port, threads=4)
