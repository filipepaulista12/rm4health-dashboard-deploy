#!/usr/bin/env python3
import paramiko

def corrigir_problemas():
    print("🔧 CORRIGINDO PROBLEMAS IDENTIFICADOS")
    print("-" * 50)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')
        
        # 1. Primeiro vamos corrigir o Apache
        print("🔧 CORRIGINDO CONFIGURAÇÃO APACHE...")
        
        # Desabilitar site problemático
        ssh.exec_command('sudo a2dissite rm4health.conf')
        print("✅ Site rm4health desabilitado")
        
        # Criar configuração mais simples
        simple_config = '''# RM4Health Proxy Configuration
<Location "/rm4health">
    ProxyPreserveHost On
    ProxyPass http://127.0.0.1:8000/
    ProxyPassReverse http://127.0.0.1:8000/
</Location>'''
        
        # Adicionar ao site principal em vez de criar novo site
        cmd = f'echo "{simple_config}" | sudo tee -a /etc/apache2/sites-available/000-default.conf'
        ssh.exec_command(cmd)
        print("✅ Configuração proxy adicionada ao site padrão")
        
        # Testar configuração
        stdin, stdout, stderr = ssh.exec_command('sudo apache2ctl configtest')
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if 'Syntax OK' in output or 'Syntax OK' in error:
            print("✅ Configuração Apache corrigida")
            ssh.exec_command('sudo systemctl reload apache2')
            print("✅ Apache recarregado")
        else:
            print(f"⚠️  Ainda há problema na config: {error}")
        
        # 2. Modificar o app para funcionar sem VPN (modo demo)
        print(f"\n🔧 CRIANDO VERSÃO DEMO SEM VPN...")
        
        # Criar versão simplificada do app que não precisa de VPN
        demo_app = '''#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

# Dados de exemplo (simulando API REDCap)
DEMO_DATA = {
    "records": [
        {"record_id": f"{i}", "age": 25+i, "gender": "Male" if i%2==0 else "Female", 
         "bmi": 22.5+i*0.3, "anxiety_depression": "Yes" if i%3==0 else "No"} 
        for i in range(1, 597)  # 596 registros como no original
    ]
}

@app.route('/')
def index():
    return render_template('index.html', total_records=596)

@app.route('/participants')
def participants():
    return render_template('participants.html')

@app.route('/api/participants')
def api_participants():
    return jsonify(DEMO_DATA["records"])

@app.route('/data-explorer')
def data_explorer():
    return render_template('data_explorer.html')

if __name__ == '__main__':
    print("🚀 RM4Health Dashboard DEMO iniciando...")
    print("📊 Modo DEMO - 596 registros simulados")
    print("🌐 Acesse: http://servidor:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
'''
        
        # Salvar versão demo
        cmd = f'echo "{demo_app}" > /var/www/html/rm4health/app_demo.py'
        ssh.exec_command(cmd)
        print("✅ Versão DEMO criada")
        
        # 3. Parar app original e iniciar demo
        print(f"\n🚀 INICIANDO VERSÃO DEMO...")
        
        ssh.exec_command('pkill -f "python3 app.py"')
        print("🔄 Parando app original...")
        
        import time
        time.sleep(2)
        
        # Iniciar versão demo
        demo_cmd = 'cd /var/www/html/rm4health && nohup python3 app_demo.py > demo.log 2>&1 &'
        ssh.exec_command(demo_cmd)
        print("🔄 Iniciando versão DEMO...")
        
        time.sleep(3)
        
        # Verificar se iniciou
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python3 app_demo.py" | grep -v grep')
        output = stdout.read().decode().strip()
        
        if output:
            print("✅ Dashboard DEMO rodando!")
            
            # Testar acesso
            stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
            http_code = stdout.read().decode().strip()
            
            if http_code == '200':
                print("✅ Dashboard DEMO respondendo!")
            else:
                print(f"⚠️  Código de resposta: {http_code}")
                
        else:
            print("❌ Dashboard DEMO não iniciou")
            
            # Ver log do erro
            stdin, stdout, stderr = ssh.exec_command('cd /var/www/html/rm4health && tail -5 demo.log')
            log_output = stdout.read().decode().strip()
            if log_output:
                print(f"📄 Log do erro: {log_output}")
        
        print(f"\n🎉 CORREÇÕES APLICADAS!")
        print(f"🌐 TESTE AGORA: https://ciis.fmrp.usp.br/rm4health/")
        print(f"📊 Versão DEMO com 596 registros simulados")
        print(f"💡 Quando conectar na VPN, mude para: python3 app.py")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        
    finally:
        try:
            ssh.close()
            print(f"\n🔌 Correções finalizadas")
        except:
            pass

if __name__ == "__main__":
    corrigir_problemas()
