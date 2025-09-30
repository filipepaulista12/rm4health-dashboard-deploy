import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('MUDANDO PARA PORTA 8081')

# Parar tudo na 8080
stdin, stdout, stderr = ssh.exec_command('sudo pkill -f "python3.*app.py"')
stdout.read()

import time
time.sleep(2)

# Iniciar na 8081
stdin, stdout, stderr = ssh.exec_command('cd /var/www/html/rm4health && python3 -c "from app import app; app.run(host=\'0.0.0.0\', port=8081)" &')
stdout.read()

time.sleep(3)

# Testar
stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8081 | head -2')
result = stdout.read().decode()
print(f'RESULTADO: {result}')

ssh.close()
print('TESTE: http://200.144.254.4:8081')
