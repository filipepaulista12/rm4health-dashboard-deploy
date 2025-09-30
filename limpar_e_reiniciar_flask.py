import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('🧹 LIMPANDO PROCESSOS FLASK DUPLICADOS')
print()

# Parar TODOS os processos do app.py do rm4health
stdin, stdout, stderr = ssh.exec_command('sudo pkill -f "/var/www/html/rm4health/app.py"')
stdout.read()
print('🛑 Parando processos Flask rm4health...')

time.sleep(3)

# Verificar se ainda há algo na porta 8080
stdin, stdout, stderr = ssh.exec_command('sudo lsof -i :8080')
remaining = stdout.read().decode()
if remaining.strip():
    print('⚠️  Ainda há processos na porta 8080:')
    print(remaining)
    
    # Force kill se necessário
    stdin, stdout, stderr = ssh.exec_command('sudo fuser -k 8080/tcp')
    stdout.read()
    print('💥 Force kill na porta 8080')
    time.sleep(2)
else:
    print('✅ Porta 8080 liberada')

print()
print('🚀 INICIANDO FLASK LIMPO')

# Iniciar Flask limpo em background
start_command = '''
cd /var/www/html/rm4health && 
nohup python3 -c "
import sys
sys.path.insert(0, '.')
from app import app
if __name__ == '__main__':
    print('🎯 RM4Health Flask starting on port 8080...')
    app.run(host='0.0.0.0', port=8080, debug=False)
" > flask_clean.log 2>&1 &
'''

stdin, stdout, stderr = ssh.exec_command(start_command)
stdout.read()
print('🔄 Iniciando Flask limpo...')

time.sleep(5)

# Verificar se está rodando
stdin, stdout, stderr = ssh.exec_command('ps aux | grep python3 | grep app')
new_process = stdout.read().decode()
if 'python3' in new_process and 'grep' not in new_process:
    print('✅ Flask iniciado:')
    print(new_process.strip())
    
    # Testar resposta
    stdin, stdout, stderr = ssh.exec_command('curl -s -I http://127.0.0.1:8080')
    response = stdout.read().decode()
    if '200 OK' in response:
        print('✅ Flask respondendo HTTP 200')
        
        # Testar o subdomínio via curl local
        stdin, stdout, stderr = ssh.exec_command('curl -s -I -H "Host: rm4health.ciis.fmrp.usp.br" http://127.0.0.1')
        subdomain_response = stdout.read().decode()
        print()
        print('🌐 Teste do subdomínio:')
        print(subdomain_response[:200])
        
    else:
        print(f'⚠️  Resposta: {response[:100]}')
else:
    print('❌ Flask não iniciou - verificando log...')
    stdin, stdout, stderr = ssh.exec_command('tail -10 /var/www/html/rm4health/flask_clean.log')
    log = stdout.read().decode()
    print(f'Log: {log}')

ssh.close()
