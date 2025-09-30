import paramiko
import time
import sys

print('PROCURANDO PORTA LIVRE')
print('Tentando conectar ao servidor remoto...')

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Aumentar timeout para 30 segundos
    ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA', timeout=30)
    print('Conexão SSH estabelecida com sucesso!')
except Exception as e:
    print(f'ERRO: Não foi possível conectar ao servidor: {e}')
    print('Verifique se o servidor está online e acessível pela rede.')
    sys.exit(1)

# Ver portas ocupadas
stdin, stdout, stderr = ssh.exec_command('sudo netstat -tulnp | grep LISTEN | grep -E ":80[0-9][0-9]"')
ports = stdout.read().decode()
print('Portas 80xx ocupadas:')
print(ports)

# Testar porta 8085
stdin, stdout, stderr = ssh.exec_command('sudo lsof -i :8085')
port8085 = stdout.read().decode()
if port8085.strip():
    print('8085 ocupada')
    # Tentar 8090
    stdin, stdout, stderr = ssh.exec_command('sudo lsof -i :8090')
    port8090 = stdout.read().decode()
    if not port8090.strip():
        porta = 8090
    else:
        porta = 8099  # ultima tentativa
else:
    porta = 8085

print(f'USANDO PORTA {porta}')

# Parar tudo
stdin, stdout, stderr = ssh.exec_command('sudo pkill -f "python3.*app.py"')
stdout.read()

import time
time.sleep(2)

# Iniciar na porta escolhida
stdin, stdout, stderr = ssh.exec_command(f'cd /var/www/html/rm4health && nohup python3 -c "from app import app; app.run(host=\'0.0.0.0\', port={porta})" > flask{porta}.log 2>&1 &')
stdout.read()

time.sleep(4)

# Testar
print(f'Verificando se a aplicação está respondendo na porta {porta}...')
stdin, stdout, stderr = ssh.exec_command(f'curl -s http://127.0.0.1:{porta} | head -1')
result = stdout.read().decode()
error = stderr.read().decode()

if result:
    print(f'RESULTADO: {result}')
    print(f'URL FINAL: http://200.144.254.4:{porta}')
    
    # Verificar regras de firewall
    print('Verificando regras de firewall...')
    stdin, stdout, stderr = ssh.exec_command('sudo ufw status | grep 8099')
    firewall_status = stdout.read().decode()
    
    if not firewall_status.strip():
        print('Adicionando regra no firewall...')
        stdin, stdout, stderr = ssh.exec_command(f'sudo ufw allow {porta}/tcp')
        stdout.read()
        
        print('Recarregando firewall...')
        stdin, stdout, stderr = ssh.exec_command('sudo ufw reload')
        stdout.read()
        
        print(f'Porta {porta} liberada no firewall!')
else:
    print(f'ERRO: Aplicação não está respondendo na porta {porta}')
    if error:
        print(f'Erro: {error}')
    print('Tentando verificar logs...')
    stdin, stdout, stderr = ssh.exec_command(f'tail -n 20 /var/www/html/rm4health/flask{porta}.log')
    log = stdout.read().decode()
    print(f'Log da aplicação: {log}')

ssh.close()
print('Conexão encerrada.')
