#!/usr/bin/env python3
import paramiko

def testar_dashboard():
    hostname = '200.144.254.4'
    port = 22
    username = 'ubuntu'
    password = 'vFpyJS4FA'
    
    print("🧪 TESTANDO DASHBOARD NO SERVIDOR")
    print("-" * 40)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("🔌 Conectando...")
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # Testar importação do app
        cmd_test = 'cd /var/www/html/rm4health && source venv/bin/activate && python3 -c "from app import app; print(\'App OK\')"'
        print("🔄 Testando importação do Flask app...")
        
        stdin, stdout, stderr = ssh.exec_command(cmd_test, timeout=30)
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if "App OK" in output:
            print("✅ Flask app importado com sucesso!")
        else:
            print(f"❌ Erro na importação: {error}")
            
        # Iniciar servidor em background por 10 segundos
        print("\n🚀 Iniciando servidor temporariamente...")
        cmd_start = 'cd /var/www/html/rm4health && timeout 10s bash -c "source venv/bin/activate && python3 app.py --host=0.0.0.0 --port=8000" &'
        ssh.exec_command(cmd_start)
        
        print("🌐 Dashboard deve estar acessível em:")
        print("   https://ciis.fmrp.usp.br/rm4health/")
        print("   (se proxy reverso estiver configurado)")
        print("\n📋 Para iniciar permanentemente:")
        print("   ssh ubuntu@200.144.254.4")
        print("   cd /var/www/html/rm4health")
        print("   nohup ./start.sh &")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        
    finally:
        try:
            ssh.close()
            print("\n🔌 Teste concluído")
        except:
            pass

if __name__ == "__main__":
    testar_dashboard()
