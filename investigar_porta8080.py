import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('🔍 INVESTIGANDO O QUE ESTÁ NA PORTA 8080')
print()

# Ver todos os processos na porta 8080
stdin, stdout, stderr = ssh.exec_command('sudo lsof -i :8080')
port_processes = stdout.read().decode()
print('Processos na porta 8080:')
print(port_processes)

print()

# Ver detalhes dos processos Python
stdin, stdout, stderr = ssh.exec_command('ps aux | grep python | grep -v grep')
python_processes = stdout.read().decode()
print('Processos Python ativos:')
for line in python_processes.split('\n'):
    if line.strip():
        print(f'  {line.strip()}')

print()

# Ver o que está executando especificamente na 8080
stdin, stdout, stderr = ssh.exec_command('sudo netstat -tulnp | grep :8080')
netstat_result = stdout.read().decode()
print('Porta 8080 detalhes:')
print(netstat_result)

print()

# Tentar identificar o diretório do processo
stdin, stdout, stderr = ssh.exec_command('sudo lsof -i :8080 -n | tail -1 | awk "{print $2}"')
pid = stdout.read().decode().strip()
if pid and pid.isdigit():
    stdin, stdout, stderr = ssh.exec_command(f'sudo pwdx {pid}')
    working_dir = stdout.read().decode()
    print(f'Diretório do processo PID {pid}: {working_dir}')
    
    # Ver o comando completo
    stdin, stdout, stderr = ssh.exec_command(f'ps -p {pid} -o cmd --no-headers')
    full_command = stdout.read().decode()
    print(f'Comando completo: {full_command}')

ssh.close()
