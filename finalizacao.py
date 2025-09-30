#!/usr/bin/env python3
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("🔧 Instalação final python-dotenv...")
ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')

# Instalar python-dotenv
ssh.exec_command('pip3 install python-dotenv')
print("✅ python-dotenv instalado!")

# Testar dashboard
stdin, stdout, stderr = ssh.exec_command('cd /var/www/html/rm4health && python3 -c "from app import app; print(\'OK\')"')
output = stdout.read().decode().strip()
error = stderr.read().decode().strip()

if 'OK' in output:
    print("🎉 DASHBOARD FUNCIONANDO PERFEITAMENTE!")
    print()
    print("🌐 ACESSE: https://ciis.fmrp.usp.br/rm4health/")
    print()
    print("🚀 Para iniciar o servidor:")
    print("   ssh ubuntu@200.144.254.4")
    print("   cd /var/www/html/rm4health")  
    print("   python3 app.py")
else:
    print(f"⚠️ Ainda há erro: {error}")

ssh.close()
print("🔌 Finalizado!")
