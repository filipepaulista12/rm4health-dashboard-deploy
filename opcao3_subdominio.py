#!/usr/bin/env python3
"""
OPÇÃO 3 - SUBDOMÍNIO DEDICADO PARA RM4HEALTH
============================================

Criar: rm4health.ciis.fmrp.usp.br
- Configuração independente
- Sem interferir com site principal
- Mais profissional
"""

import paramiko
import time

def criar_subdominio_dedicado():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')
    
    print("🌐 CRIANDO SUBDOMÍNIO DEDICADO: rm4health.ciis.fmrp.usp.br")
    print()
    
    # 1. Criar configuração do subdomínio
    config_subdominio = """<VirtualHost *:80>
    ServerName rm4health.ciis.fmrp.usp.br
    DocumentRoot /var/www/html/rm4health
    
    # Proxy para Flask no port 8080
    ProxyPreserveHost On
    ProxyRequests Off
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/
    
    # Logs específicos do subdomínio
    ErrorLog ${APACHE_LOG_DIR}/rm4health_error.log
    CustomLog ${APACHE_LOG_DIR}/rm4health_access.log combined
    
    # Headers de segurança
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
</VirtualHost>"""
    
    # Criar o arquivo de configuração
    stdin, stdout, stderr = ssh.exec_command(f"""
sudo tee /etc/apache2/sites-available/rm4health-subdomain.conf > /dev/null << 'EOF'
{config_subdominio}
EOF
    """)
    stdout.read()
    print("✅ Configuração do subdomínio criada")
    
    # 2. Habilitar módulos necessários
    modules = ['proxy', 'proxy_http', 'headers']
    for module in modules:
        stdin, stdout, stderr = ssh.exec_command(f'sudo a2enmod {module}')
        result = stdout.read().decode()
        print(f"📦 Módulo {module}: {result.strip() if result else 'OK'}")
    
    # 3. Habilitar o site
    stdin, stdout, stderr = ssh.exec_command('sudo a2ensite rm4health-subdomain.conf')
    result = stdout.read().decode()
    print(f"🔧 Habilitando subdomínio: {result}")
    
    # 4. Testar configuração
    stdin, stdout, stderr = ssh.exec_command('sudo apache2ctl configtest')
    config_out = stdout.read().decode()
    config_err = stderr.read().decode()
    
    if 'Syntax OK' in config_err:
        print("✅ Configuração OK")
        
        # 5. Recarregar Apache
        stdin, stdout, stderr = ssh.exec_command('sudo systemctl reload apache2')
        stdout.read()
        print("🔄 Apache recarregado")
        
        time.sleep(2)
        
        # 6. Verificar se Apache ainda está ativo
        stdin, stdout, stderr = ssh.exec_command('systemctl is-active apache2')
        status = stdout.read().decode().strip()
        print(f"Status Apache: {status}")
        
        if status == 'active':
            print("🎉 SUBDOMÍNIO CONFIGURADO COM SUCESSO!")
            print()
            print("📋 PRÓXIMOS PASSOS:")
            print("1. Configurar DNS: rm4health.ciis.fmrp.usp.br → 200.144.254.4")
            print("2. Iniciar dashboard Flask na porta 8080")
            print("3. Acessar: http://rm4health.ciis.fmrp.usp.br")
            
            # Verificar se Flask está rodando
            stdin, stdout, stderr = ssh.exec_command('ps aux | grep python3 | grep 8080')
            flask_proc = stdout.read().decode()
            if flask_proc.strip():
                print("✅ Flask já está rodando na porta 8080")
            else:
                print("⚠️  Flask precisa ser iniciado na porta 8080")
                
        else:
            print(f"❌ Problema com Apache: {status}")
    else:
        print(f"❌ Erro na configuração: {config_err}")
    
    ssh.close()

if __name__ == "__main__":
    criar_subdominio_dedicado()
