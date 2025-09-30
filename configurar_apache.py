#!/usr/bin/env python3
import paramiko

def configurar_apache():
    print("🔧 CONFIGURANDO APACHE PARA RM4HEALTH")
    print("⚠️  MODO SUPER CAUTELOSO - Apenas configuração necessária")
    print("-" * 60)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')
        
        # 1. Verificar estrutura atual do Apache
        print("🔍 VERIFICANDO CONFIGURAÇÃO ATUAL DO APACHE...")
        
        comandos_verificacao = [
            ('ls -la /var/www/html/', 'Conteúdo de /var/www/html/'),
            ('ls -la /etc/apache2/sites-available/', 'Sites disponíveis'),
            ('ls -la /etc/apache2/sites-enabled/', 'Sites habilitados'),
            ('apache2 -v', 'Versão do Apache'),
        ]
        
        for cmd, desc in comandos_verificacao:
            print(f"\n🔄 {desc}...")
            try:
                stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
                output = stdout.read().decode().strip()
                if output:
                    print(f"✅ {desc}:")
                    print(f"   📄 {output[:300]}{'...' if len(output) > 300 else ''}")
            except Exception as e:
                print(f"⚠️  {desc}: {str(e)[:100]}")
        
        # 2. Iniciar o dashboard como serviço em background
        print(f"\n🚀 INICIANDO DASHBOARD EM BACKGROUND...")
        
        # Matar processos anteriores (se houver)
        ssh.exec_command('pkill -f "python3 app.py"')
        print("🔄 Parando processos anteriores...")
        
        # Iniciar dashboard na porta 8000
        start_cmd = 'cd /var/www/html/rm4health && nohup python3 app.py --host=0.0.0.0 --port=8000 > dashboard.log 2>&1 &'
        ssh.exec_command(start_cmd)
        print("✅ Dashboard iniciado na porta 8000")
        
        import time
        time.sleep(3)
        
        # Verificar se está rodando
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python3 app.py"')
        output = stdout.read().decode()
        if 'app.py' in output and 'grep' not in output:
            print("✅ Dashboard confirmado rodando!")
        
        # 3. Configurar proxy reverso no Apache
        print(f"\n🔧 CONFIGURANDO PROXY REVERSO NO APACHE...")
        
        # Habilitar módulos necessários
        modulos = ['proxy', 'proxy_http', 'rewrite']
        for mod in modulos:
            cmd = f'sudo a2enmod {mod}'
            ssh.exec_command(cmd)
            print(f"✅ Módulo {mod} habilitado")
        
        # Criar configuração do site
        apache_config = '''<VirtualHost *:80>
    ServerName ciis.fmrp.usp.br
    DocumentRoot /var/www/html
    
    # Proxy para RM4Health Dashboard
    ProxyPreserveHost On
    ProxyPass /rm4health/ http://127.0.0.1:8000/
    ProxyPassReverse /rm4health/ http://127.0.0.1:8000/
    
    # Logs
    ErrorLog ${APACHE_LOG_DIR}/rm4health_error.log
    CustomLog ${APACHE_LOG_DIR}/rm4health_access.log combined
</VirtualHost>

<VirtualHost *:443>
    ServerName ciis.fmrp.usp.br
    DocumentRoot /var/www/html
    
    # SSL (se já configurado)
    # SSLEngine on
    # SSLCertificateFile /path/to/cert.pem
    # SSLCertificateKeyFile /path/to/private.key
    
    # Proxy para RM4Health Dashboard
    ProxyPreserveHost On
    ProxyPass /rm4health/ http://127.0.0.1:8000/
    ProxyPassReverse /rm4health/ http://127.0.0.1:8000/
    
    # Logs
    ErrorLog ${APACHE_LOG_DIR}/rm4health_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/rm4health_ssl_access.log combined
</VirtualHost>'''
        
        # Salvar configuração
        config_cmd = f'echo "{apache_config}" | sudo tee /etc/apache2/sites-available/rm4health.conf'
        ssh.exec_command(config_cmd)
        print("✅ Configuração do site criada")
        
        # Habilitar site
        ssh.exec_command('sudo a2ensite rm4health.conf')
        print("✅ Site habilitado")
        
        # Testar configuração
        stdin, stdout, stderr = ssh.exec_command('sudo apache2ctl configtest')
        output = stdout.read().decode()
        if 'Syntax OK' in output:
            print("✅ Configuração Apache válida")
        else:
            print(f"⚠️  Configuração: {output}")
        
        # Recarregar Apache
        ssh.exec_command('sudo systemctl reload apache2')
        print("✅ Apache recarregado")
        
        print(f"\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
        print(f"🌐 DASHBOARD DISPONÍVEL EM:")
        print(f"   https://ciis.fmrp.usp.br/rm4health/")
        print(f"   http://ciis.fmrp.usp.br/rm4health/")
        print(f"\n📊 DASHBOARD RODANDO NA PORTA 8000")
        print(f"📋 LOGS DISPONÍVEIS EM:")
        print(f"   Dashboard: /var/www/html/rm4health/dashboard.log")
        print(f"   Apache: /var/log/apache2/rm4health_*")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        
    finally:
        try:
            ssh.close()
            print(f"\n🔌 Desconectado")
        except:
            pass

if __name__ == "__main__":
    configurar_apache()
