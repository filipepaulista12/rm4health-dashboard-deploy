#!/usr/bin/env python3
import paramiko
import time

def configurar_servidor():
    # Configurações do servidor
    hostname = '200.144.254.4'
    port = 22
    username = 'ubuntu'
    password = 'vFpyJS4FA'
    
    print("🔧 CONFIGURAÇÃO RM4HEALTH DASHBOARD NO SERVIDOR")
    print(f"Servidor: {hostname}:{port}")
    print("⚠️  MODO CAUTELOSO - Apenas configurações necessárias")
    print("-" * 60)
    
    try:
        # Conectar via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print("🔌 Conectando ao servidor...")
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # Função para executar comando e mostrar resultado
        def executar_comando(cmd, descricao):
            print(f"🔄 {descricao}...")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            
            # Aguardar comando terminar
            exit_status = stdout.channel.recv_exit_status()
            
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            if exit_status == 0:
                print(f"✅ {descricao} - OK")
                if output:
                    print(f"   📄 Output: {output[:200]}{'...' if len(output) > 200 else ''}")
            else:
                print(f"❌ {descricao} - ERRO (exit: {exit_status})")
                if error:
                    print(f"   ⚠️  Error: {error[:200]}{'...' if len(error) > 200 else ''}")
            
            return exit_status == 0, output, error
        
        # 1. Verificar se a pasta existe
        print("\n🔍 VERIFICAÇÃO INICIAL")
        success, output, error = executar_comando('ls -la /var/www/html/rm4health/', 'Verificando pasta rm4health')
        
        if not success:
            print("❌ Pasta rm4health não encontrada! Execute o deploy primeiro.")
            return False
        
        # 2. Atualizar sistema (cuidadosamente)
        print("\n📦 INSTALAÇÃO DE DEPENDÊNCIAS")
        executar_comando('sudo apt update', 'Atualizando lista de pacotes')
        
        # Verificar se Python3 já está instalado
        success, output, error = executar_comando('python3 --version', 'Verificando Python3')
        if success:
            print(f"✅ Python3 já instalado: {output}")
        
        # Verificar se pip3 já está instalado
        success, output, error = executar_comando('pip3 --version', 'Verificando pip3')
        if not success:
            executar_comando('sudo apt install python3-pip -y', 'Instalando pip3')
        else:
            print(f"✅ pip3 já instalado: {output}")
        
        # Instalar python3-venv se necessário
        executar_comando('sudo apt install python3-venv python3-dev -y', 'Instalando python3-venv e python3-dev')
        
        # 3. Navegar para pasta e criar ambiente virtual
        print("\n🐍 CONFIGURAÇÃO DO AMBIENTE VIRTUAL")
        
        # Verificar se venv já existe
        success, output, error = executar_comando('ls /var/www/html/rm4health/venv/', 'Verificando se venv existe')
        
        if not success:
            executar_comando('cd /var/www/html/rm4health && python3 -m venv venv', 'Criando ambiente virtual')
            time.sleep(2)
        else:
            print("✅ Ambiente virtual já existe")
        
        # 4. Instalar dependências
        print("\n📚 INSTALAÇÃO DE DEPENDÊNCIAS PYTHON")
        cmd = 'cd /var/www/html/rm4health && source venv/bin/activate && pip install -r requirements.txt'
        executar_comando(cmd, 'Instalando dependências do requirements.txt')
        
        # Instalar gunicorn para produção
        cmd_gunicorn = 'cd /var/www/html/rm4health && source venv/bin/activate && pip install gunicorn'
        executar_comando(cmd_gunicorn, 'Instalando Gunicorn')
        
        # 5. Testar aplicação
        print("\n🧪 TESTE DA APLICAÇÃO")
        cmd_test = 'cd /var/www/html/rm4health && source venv/bin/activate && python3 -c "import sys; print(sys.version)"'
        executar_comando(cmd_test, 'Testando ambiente Python')
        
        # 6. Criar script de inicialização
        print("\n📝 CRIANDO SCRIPT DE INICIALIZAÇÃO")
        
        script_start = """#!/bin/bash
cd /var/www/html/rm4health
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=production
gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 app:app
"""
        
        # Criar arquivo start.sh
        cmd_script = f'echo "{script_start}" > /var/www/html/rm4health/start.sh'
        executar_comando(cmd_script, 'Criando script start.sh')
        
        # Dar permissão de execução
        executar_comando('chmod +x /var/www/html/rm4health/start.sh', 'Dando permissão ao script')
        
        # 7. Configurar permissões finais
        print("\n🔒 CONFIGURAÇÃO DE PERMISSÕES")
        executar_comando('sudo chown -R ubuntu:www-data /var/www/html/rm4health/', 'Configurando owner dos arquivos')
        executar_comando('sudo chmod -R 755 /var/www/html/rm4health/', 'Configurando permissões dos arquivos')
        
        print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("🚀 PRÓXIMOS PASSOS:")
        print("1. Testar manualmente:")
        print("   ssh ubuntu@200.144.254.4")
        print("   cd /var/www/html/rm4health")
        print("   ./start.sh")
        print()
        print("2. Configurar proxy reverso no Nginx (se necessário)")
        print("3. Criar serviço systemd (se quiser auto-start)")
        print()
        print("🌐 URL esperada: https://ciis.fmrp.usp.br/rm4health/")
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {str(e)}")
        return False
        
    finally:
        try:
            ssh.close()
            print("🔌 Conexão SSH fechada")
        except:
            pass
            
    return True

if __name__ == "__main__":
    print("🚨 ATENÇÃO: Este script vai configurar o servidor com cuidado!")
    print("Apenas instalará Python, criará ambiente virtual e configurará o dashboard.")
    print("NÃO modificará outros arquivos ou serviços do servidor.")
    print()
    
    resposta = input("Deseja continuar? (s/N): ").lower().strip()
    if resposta in ['s', 'sim', 'y', 'yes']:
        configurar_servidor()
    else:
        print("❌ Operação cancelada pelo usuário.")
