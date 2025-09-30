import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('TESTE FINAL DO SUBDOMÍNIO')
stdin, stdout, stderr = ssh.exec_command('curl -s -H "Host: rm4health.ciis.fmrp.usp.br" http://localhost | head -5')
result = stdout.read().decode()
print(f'SUBDOMÍNIO: {result}')

ssh.close()
print('TESTE COMPLETO!')
