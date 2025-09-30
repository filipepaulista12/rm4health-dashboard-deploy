import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('🔧 CONFIGURANDO PATH NO SITE PRINCIPAL')
print('URL: http://ciis.fmrp.usp.br/rm4health')
print()

# Adicionar configuração de path no site principal
config_path = '''
# RM4Health Dashboard Path
<Location /rm4health>
    ProxyPass http://127.0.0.1:8080/
    ProxyPassReverse http://127.0.0.1:8080/
    ProxyPreserveHost On
</Location>
'''

# Encontrar o site principal e adicionar a configuração
stdin, stdout, stderr = ssh.exec_command('grep -l "ciis.fmrp.usp.br" /etc/apache2/sites-enabled/*.conf')
main_site = stdout.read().decode().strip()
print(f'Site principal: {main_site}')

if main_site:
    # Adicionar configuração no final do VirtualHost
    stdin, stdout, stderr = ssh.exec_command(f'''
sudo sed -i '/<\/VirtualHost>/i\\
\\
# RM4Health Dashboard Path\\
<Location /rm4health>\\
    ProxyPass http://127.0.0.1:8080/\\
    ProxyPassReverse http://127.0.0.1:8080/\\
    ProxyPreserveHost On\\
</Location>' "{main_site}"
    ''')
    result = stdout.read().decode()
    print('✅ Configuração adicionada')
    
    # Testar configuração
    stdin, stdout, stderr = ssh.exec_command('sudo apache2ctl configtest')
    test_result = stderr.read().decode()
    if 'Syntax OK' in test_result:
        print('✅ Configuração válida')
        
        # Recarregar Apache
        stdin, stdout, stderr = ssh.exec_command('sudo systemctl reload apache2')
        stdout.read()
        print('🔄 Apache recarregado')
        
        # Teste local
        stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1/rm4health | head -3')
        test_response = stdout.read().decode()
        print('📡 Teste local:')
        print(test_response)
        
    else:
        print(f'❌ Erro de configuração: {test_result}')
else:
    print('❌ Site principal não encontrado')

ssh.close()
print()
print('🌟 TESTE AGORA: http://ciis.fmrp.usp.br/rm4health')
