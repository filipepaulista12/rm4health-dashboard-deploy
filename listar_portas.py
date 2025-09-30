import paramiko

# Conectar ao servidor
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('🔍 IDENTIFICANDO PORTAS OCUPADAS')

# Comando para listar portas ocupadas
stdin, stdout, stderr = ssh.exec_command('sudo ss -tuln')
ports = stdout.read().decode()
print('Portas ocupadas:')
print(ports)

ssh.close()
