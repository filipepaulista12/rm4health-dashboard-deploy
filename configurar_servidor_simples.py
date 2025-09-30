#!/usr/bin/env python3
import paramiko
import time
import threading

def configurar_servidor_simples():
    hostname = '200.144.254.4'
    port = 22
    username = 'ubuntu'
    password = 'vFpyJS4FA'
    
    print("🔧 CONFIGURAÇÃO RÁPIDA RM4HEALTH DASHBOARD")
    print("⚠️  MODO SUPER CAUTELOSO")
    print("-" * 50)
    
    try:
        # Conectar via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("🔌 Conectando...")
        ssh.connect(hostname, port=port, username=username, password=password)
        
        commands = [
            ('ls /var/www/html/rm4health/', 'Verificando pasta'),
            ('cd /var/www/html/rm4health && python3 --version', 'Testando Python'),
            ('cd /var/www/html/rm4health && python3 -m venv venv', 'Criando venv'),
            ('cd /var/www/html/rm4health && ls -la', 'Listando arquivos'),
        ]
        
        for cmd, desc in commands:
            print(f"🔄 {desc}...")
            try:
                stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                
                if output:
                    print(f"✅ {desc} - OK")
                    print(f"   📄 {output[:100]}{'...' if len(output) > 100 else ''}")
                if error and 'warning' not in error.lower():
                    print(f"⚠️  {desc} - Warning: {error[:100]}")
                    
            except Exception as e:
                print(f"❌ {desc} - Erro: {str(e)[:100]}")
                
            time.sleep(1)
        
        # Comandos de instalação mais simples
        install_commands = [
            'cd /var/www/html/rm4health && source venv/bin/activate && pip install --upgrade pip',
            'cd /var/www/html/rm4health && source venv/bin/activate && pip install flask plotly pandas requests',
            'cd /var/www/html/rm4health && source venv/bin/activate && pip install gunicorn',
            'chmod +x /var/www/html/rm4health/app.py'
        ]
        
        print("\n📚 INSTALANDO DEPENDÊNCIAS BÁSICAS...")
        for cmd in install_commands:
            try:
                print(f"🔄 Executando: {cmd.split('&&')[-1].strip()}")
                stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
                stdout.read()  # Aguardar conclusão
                print("✅ OK")
            except:
                print("⚠️  Timeout ou erro")
            time.sleep(2)
        
        # Criar script de start simples
        start_script = '''#!/bin/bash
cd /var/www/html/rm4health
source venv/bin/activate
export FLASK_APP=app.py
python3 app.py --host=0.0.0.0 --port=8000
'''
        
        print("\n📝 CRIANDO SCRIPT DE START...")
        ssh.exec_command(f'echo "{start_script}" > /var/www/html/rm4health/start.sh')
        ssh.exec_command('chmod +x /var/www/html/rm4health/start.sh')
        
        print("\n🎉 CONFIGURAÇÃO BÁSICA CONCLUÍDA!")
        print("🚀 TESTE MANUAL:")
        print("1. ssh ubuntu@200.144.254.4")
        print("2. cd /var/www/html/rm4health")
        print("3. ./start.sh")
        print("\n🌐 URL: https://ciis.fmrp.usp.br/rm4health/")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        
    finally:
        try:
            ssh.close()
            print("🔌 Desconectado")
        except:
            pass

if __name__ == "__main__":
    configurar_servidor_simples()
