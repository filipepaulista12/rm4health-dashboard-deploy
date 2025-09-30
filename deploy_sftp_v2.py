#!/usr/bin/env python3
import paramiko
import os
import sys
from stat import S_ISDIR

def sftp_deploy():
    # Configurações do servidor
    hostname = '200.144.254.4'
    port = 22
    username = 'ubuntu'
    password = 'vFpyJS4FA'
    remote_path = '/var/www/html'
    local_path = r'C:\Users\up739088\Desktop\FMUP\rm4isep\redcap-dashboard-simples'
    
    print("🚀 DEPLOY RM4HEALTH DASHBOARD")
    print(f"Servidor: {hostname}:{port}")
    print(f"Diretório remoto: {remote_path}/rm4health")
    print(f"Diretório local: {local_path}")
    print("-" * 50)
    
    try:
        # Conectar via SSH/SFTP
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print("🔌 Conectando ao servidor...")
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # Primeiro tentar via SSH com sudo
        print("🔑 Criando pasta com sudo...")
        stdin, stdout, stderr = ssh.exec_command('sudo mkdir -p /var/www/html/rm4health')
        result = stdout.read().decode()
        error = stderr.read().decode()
        
        if error:
            print(f"⚠️  SSH Error: {error}")
        
        # Dar permissões corretas
        print("🔒 Configurando permissões...")
        ssh.exec_command('sudo chown ubuntu:www-data /var/www/html/rm4health')
        ssh.exec_command('sudo chmod 755 /var/www/html/rm4health')
        
        # Agora usar SFTP
        sftp = ssh.open_sftp()
        
        # Navegar para /var/www/html
        print("📁 Navegando para /var/www/html...")
        sftp.chdir('/var/www/html')
        
        # Verificar se pasta foi criada
        try:
            sftp.stat('rm4health')
            print("✅ Pasta rm4health existe!")
            sftp.chdir('rm4health')
        except FileNotFoundError:
            print("❌ Pasta rm4health não foi criada")
            return False
            
        print("📁 Dentro de /var/www/html/rm4health")
        
        # Lista de arquivos para upload
        files_to_upload = [
            'app.py',
            'analytics.py', 
            'config.py',
            'data_processor.py',
            'redcap_client.py',
            'requirements.txt'
        ]
        
        # Upload dos arquivos principais
        print("📤 Fazendo upload dos arquivos...")
        for file in files_to_upload:
            local_file = os.path.join(local_path, file)
            if os.path.exists(local_file):
                print(f"  ⬆️  {file}")
                sftp.put(local_file, file)
            else:
                print(f"  ❌ {file} não encontrado")
        
        # Criar e upload da pasta templates
        try:
            sftp.mkdir('templates')
            print("✅ Pasta templates criada")
        except:
            print("⚠️  Pasta templates já existe")
            
        templates_local = os.path.join(local_path, 'templates')
        if os.path.exists(templates_local):
            for template in os.listdir(templates_local):
                template_path = os.path.join(templates_local, template)
                if os.path.isfile(template_path):
                    print(f"  ⬆️  templates/{template}")
                    sftp.put(template_path, f'templates/{template}')
        
        # Criar e upload da pasta static (se existir)
        static_local = os.path.join(local_path, 'static')
        if os.path.exists(static_local):
            try:
                sftp.mkdir('static')
                print("✅ Pasta static criada")
            except:
                print("⚠️  Pasta static já existe")
                
            for static_file in os.listdir(static_local):
                static_path = os.path.join(static_local, static_file)
                if os.path.isfile(static_path):
                    print(f"  ⬆️  static/{static_file}")
                    sftp.put(static_path, f'static/{static_file}')
        
        print("\n🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print(f"🌐 URL: https://ciis.fmrp.usp.br/rm4health/")
        print("\n📋 Próximos passos no servidor:")
        print("1. sudo apt update && sudo apt install python3-pip python3-venv")
        print("2. cd /var/www/html/rm4health")
        print("3. python3 -m venv venv")
        print("4. source venv/bin/activate")
        print("5. pip install -r requirements.txt")
        print("6. Configurar WSGI server (Gunicorn)")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False
        
    finally:
        try:
            sftp.close()
            ssh.close()
            print("🔌 Conexão fechada")
        except:
            pass
            
    return True

if __name__ == "__main__":
    sftp_deploy()
