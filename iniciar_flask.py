import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

print('🚀 INICIANDO DASHBOARD FLASK NA PORTA 8080')
print()

# Parar qualquer processo na porta 8080
stdin, stdout, stderr = ssh.exec_command('sudo pkill -f "python.*8080"')
stdout.read()
print('🧹 Limpeza de processos anteriores')

import time
time.sleep(2)

# Iniciar Flask em background na porta 8080
start_command = '''
cd /var/www/html/rm4health && 
nohup python3 app.py > flask.log 2>&1 &
'''
stdin, stdout, stderr = ssh.exec_command(start_command)
stdout.read()
print('🔄 Iniciando Flask...')

time.sleep(5)

# Verificar se está rodando
stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python3 app.py"')
process_list = stdout.read().decode()
if 'app.py' in process_list and 'grep' not in process_list:
    print('✅ Flask iniciado com sucesso!')
    
    # Testar se responde na porta 8080
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080')
    response_code = stdout.read().decode().strip()
    print(f'📡 Teste local (porta 8080): HTTP {response_code}')
    
    if response_code == '200':
        print('🎯 Dashboard respondendo corretamente!')
        print()
        print('🌟 CONFIGURAÇÃO COMPLETA!')
        print('📍 URL: http://rm4health.ciis.fmrp.usp.br')
        print('💡 Aguardando configuração DNS...')
    else:
        print(f'⚠️  Dashboard iniciou mas resposta: {response_code}')
else:
    print('❌ Flask não iniciou - verificando log...')
    stdin, stdout, stderr = ssh.exec_command('tail -5 /var/www/html/rm4health/flask.log')
    log = stdout.read().decode()
    print(f'Log: {log}')

ssh.close()
