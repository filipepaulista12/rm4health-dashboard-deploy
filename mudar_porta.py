import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('🔧 MUDANDO FLASK PARA PORTA 8081')
print()

# 1. Parar Flask atual
stdin, stdout, stderr = ssh.exec_command('sudo pkill -f "python3.*app.py"')
stdout.read()
print('🛑 Parando Flask atual')

import time
time.sleep(2)

# 2. Modificar app.py para usar porta 8081
stdin, stdout, stderr = ssh.exec_command("""
cd /var/www/html/rm4health && 
sed -i 's/port=8080/port=8081/g' app.py && 
grep -n "port=" app.py | head -3
""")
result = stdout.read().decode()
print(f'✏️  Modificando porta: {result}')

# 3. Iniciar Flask na porta 8081
stdin, stdout, stderr = ssh.exec_command('cd /var/www/html/rm4health && nohup python3 app.py > flask_8081.log 2>&1 &')
stdout.read()
print('🚀 Iniciando Flask na porta 8081')

time.sleep(3)

# 4. Testar
stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8081 | grep -i "title\\|rm4health" | head -2')
test_result = stdout.read().decode()
print(f'✅ Teste porta 8081: {test_result}')

# 5. Ver se porta está ocupada
stdin, stdout, stderr = ssh.exec_command('sudo lsof -i :8081')
port_check = stdout.read().decode()
if port_check.strip():
    print('✅ Flask rodando na porta 8081')
    print()
    print('🌟 ACESSE AGORA: http://200.144.254.4:8081')
else:
    print('❌ Problema - verificando log...')
    stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/html/rm4health/flask_8081.log')
    log = stdout.read().decode()
    print(f'Log: {log}')

ssh.close()
