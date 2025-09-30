import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('🔍 VERIFICAÇÃO REAL - SEM MENTIRAS')
print()

# 1. Ver EXATAMENTE o que está na porta 8080
stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8080 | grep -i "title\\|simposio\\|rm4health" | head -5')
port_content = stdout.read().decode()
print(f'Porta 8080 REAL: {port_content}')

# 2. Ver todos os processos Python
stdin, stdout, stderr = ssh.exec_command('ps aux | grep python | grep -v grep')
all_python = stdout.read().decode()
print('\nTODOS os processos Python:')
print(all_python)

# 3. Ver especificamente o que está na porta 8080
stdin, stdout, stderr = ssh.exec_command('sudo lsof -i :8080')
port_8080 = stdout.read().decode()
print('\nO que REALMENTE está na porta 8080:')
print(port_8080)

# 4. Procurar nosso Flask
stdin, stdout, stderr = ssh.exec_command('find /var/www -name "app.py" -exec ls -la {} \;')
flask_files = stdout.read().decode()
print('\nArquivos app.py encontrados:')
print(flask_files)

ssh.close()
