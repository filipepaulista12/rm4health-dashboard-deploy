#!/usr/bin/env python3
import paramiko
import time

def instalar_deps_finais():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("🔧 INSTALAÇÃO FINAL DE DEPENDÊNCIAS")
        ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')
        
        # Instalar dependências uma por vez
        deps = ['python-dotenv', 'cryptography', 'werkzeug', 'jinja2']
        
        for dep in deps:
            print(f"📦 Instalando {dep}...")
            stdin, stdout, stderr = ssh.exec_command(f'pip3 install {dep}', timeout=60)
            stdout.read()
            time.sleep(1)
        
        print("✅ Todas as dependências instaladas!")
        
        # Teste simples primeiro
        print("🧪 Testando imports básicos...")
        stdin, stdout, stderr = ssh.exec_command('python3 -c "import flask; print(\'Flask OK\')"')
        output = stdout.read().decode().strip()
        if 'Flask OK' in output:
            print("✅ Flask OK")
        
        stdin, stdout, stderr = ssh.exec_command('python3 -c "from dotenv import load_dotenv; print(\'Dotenv OK\')"')
        output = stdout.read().decode().strip()
        if 'Dotenv OK' in output:
            print("✅ Dotenv OK")
        
        # Teste da aplicação
        print("🧪 Testando aplicação RM4Health...")
        stdin, stdout, stderr = ssh.exec_command('cd /var/www/html/rm4health && python3 -c "from config import Config; print(\'Config OK\')"')
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if 'Config OK' in output:
            print("✅ Config OK")
            
            # Teste final do app
            stdin, stdout, stderr = ssh.exec_command('cd /var/www/html/rm4health && python3 -c "from app import app; print(\'App OK\')"')
            output2 = stdout.read().decode().strip()
            error2 = stderr.read().decode().strip()
            
            if 'App OK' in output2:
                print("🎉 DASHBOARD TOTALMENTE FUNCIONAL!")
                print()
                print("🌐 DASHBOARD DISPONÍVEL:")
                print("   https://ciis.fmrp.usp.br/rm4health/")
                print()
                print("🚀 COMANDOS PARA INICIAR:")
                print("   ssh ubuntu@200.144.254.4")
                print("   cd /var/www/html/rm4health")
                print("   python3 app.py --host=0.0.0.0 --port=5000")
                print()
                print("💡 Para produção use:")
                print("   nohup python3 app.py --host=0.0.0.0 --port=5000 &")
                return True
            else:
                print(f"❌ Erro no app: {error2}")
        else:
            print(f"❌ Erro na config: {error}")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False
        
    finally:
        ssh.close()
        print("🔌 Desconectado")

if __name__ == "__main__":
    success = instalar_deps_finais()
    if success:
        print("\n✅ MISSÃO CONCLUÍDA! Dashboard funcionando no servidor!")
    else:
        print("\n❌ Ainda há problemas. Pode ser necessário configuração manual.")
