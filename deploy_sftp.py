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
        sftp = ssh.open_sftp()
        
        # Navegar para /var/www/html
        print("📁 Navegando para /var/www/html...")
        sftp.chdir('/var/www/html')
        
        # Listar conteúdo atual (para verificar)
        print("📋 Conteúdo atual de /var/www/html:")
        items = sftp.listdir_attr('.')
        for item in items:
            if S_ISDIR(item.st_mode):
                print(f"  📁 {item.filename}/")
            else:
                print(f"  📄 {item.filename}")
        
        # Criar pasta rm4health se não existir
        try:
            sftp.stat('rm4health')
            print("⚠️  Pasta rm4health já existe!")
        except FileNotFoundError:
            print("✅ Criando pasta rm4health...")
            sftp.mkdir('rm4health')
            
        # Entrar na pasta rm4health
        sftp.chdir('rm4health')
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
        print("\n📋 Próximos passos:")
        print("1. Instalar Python e dependências no servidor")
        print("2. Configurar WSGI (Gunicorn/uWSGI)")
        print("3. Configurar proxy reverso (Nginx)")
        
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
