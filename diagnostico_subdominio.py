import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('🔍 TESTANDO SUBDOMÍNIO - DIAGNÓSTICO REAL')
print()

# 1. Testar se o DNS resolve
stdin, stdout, stderr = ssh.exec_command('nslookup rm4health.ciis.fmrp.usp.br')
dns_result = stdout.read().decode()
print('DNS lookup:')
print(dns_result)

# 2. Ver sites do Apache
stdin, stdout, stderr = ssh.exec_command('apache2ctl -S | grep -A5 -B5 rm4health')
apache_sites = stdout.read().decode()
print('\nSites Apache com rm4health:')
print(apache_sites)

# 3. Ver se arquivo de configuração existe mesmo
stdin, stdout, stderr = ssh.exec_command('cat /etc/apache2/sites-available/rm4health-subdomain.conf')
config_content = stdout.read().decode()
print('\nConteúdo da configuração:')
print(config_content[:500])

# 4. Status do Apache
stdin, stdout, stderr = ssh.exec_command('systemctl is-active apache2')
apache_status = stdout.read().decode().strip()
print(f'\nApache status: {apache_status}')

ssh.close()
