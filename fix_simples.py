import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('AÇÃO 1: Parando processos na porta 8080')
stdin, stdout, stderr = ssh.exec_command('sudo pkill -f "python3.*app.py"')
stdout.read()

print('AÇÃO 2: Iniciando Flask limpo')
stdin, stdout, stderr = ssh.exec_command('cd /var/www/html/rm4health && python3 app.py &')
stdout.read()

print('AÇÃO 3: Testando')
import time
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8080 | head -5')
result = stdout.read().decode()
print(f'RESULTADO: {result}')

ssh.close()
print('PRONTO!')
