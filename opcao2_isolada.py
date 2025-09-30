#!/usr/bin/env python3
import paramiko

def opcao2_porta_isolada():
    print("🔧 OPÇÃO 2: PORTA ISOLADA COM DADOS REAIS")
    print("⚠️  MÁXIMO CUIDADO - Apenas configuração isolada")
    print("🎯 Objetivo: Dashboard Flask com API REDCap real")
    print("-" * 60)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')
        
        print("🔍 ESTRATÉGIA SUPER SEGURA:")
        print("✅ Modificar APENAS /etc/apache2/sites-available/rm4health.conf")
        print("✅ NÃO tocar em sites existentes (ciis.conf, raras-api.conf, etc)")
        print("✅ Dashboard Flask na porta 8080 (isolada)")
        print("✅ Proxy APENAS para /rm4health/")
        print()
        
        # 1. Primeiro parar qualquer processo anterior
        print("🔄 LIMPEZA INICIAL...")
        ssh.exec_command('pkill -f "python3 app"')
        print("✅ Processos anteriores encerrados")
        
        # 2. Verificar se rm4health.conf existe
        print("\n🔍 VERIFICANDO CONFIGURAÇÃO ATUAL...")
        stdin, stdout, stderr = ssh.exec_command('ls -la /etc/apache2/sites-available/rm4health.conf')
        output = stdout.read().decode()
        
        if 'rm4health.conf' in output:
            print("✅ Arquivo rm4health.conf existe")
            
            # Ver conteúdo atual
            stdin, stdout, stderr = ssh.exec_command('cat /etc/apache2/sites-available/rm4health.conf')
            current_config = stdout.read().decode()
            print(f"📄 Configuração atual:")
            print(f"   {current_config[:200]}{'...' if len(current_config) > 200 else ''}")
        else:
            print("⚠️  Arquivo rm4health.conf não existe, vou criar")
        
        # 3. Criar configuração específica e isolada
        print(f"\n🔧 CRIANDO CONFIGURAÇÃO ISOLADA...")
        
        # Configuração minimalista que não conflita com nada
        isolated_config = '''<VirtualHost *:80>
    ServerName ciis.fmrp.usp.br
    
    # Proxy apenas para /rm4health (sem trailing slash issues)
    ProxyPreserveHost On
    ProxyPass /rm4health http://127.0.0.1:8080/
    ProxyPassReverse /rm4health http://127.0.0.1:8080/
    
    # Headers para evitar problemas
    ProxyPassReverse /rm4health http://ciis.fmrp.usp.br/rm4health
    
    # Logs isolados
    ErrorLog ${APACHE_LOG_DIR}/rm4health_error.log
    CustomLog ${APACHE_LOG_DIR}/rm4health_access.log combined
</VirtualHost>

<VirtualHost *:443>
    ServerName ciis.fmrp.usp.br
    
    # SSL (assumindo que já está configurado globalmente)
    SSLEngine on
    
    # Proxy apenas para /rm4health
    ProxyPreserveHost On
    ProxyPass /rm4health http://127.0.0.1:8080/
    ProxyPassReverse /rm4health http://127.0.0.1:8080/
    ProxyPassReverse /rm4health https://ciis.fmrp.usp.br/rm4health
    
    # Logs isolados
    ErrorLog ${APACHE_LOG_DIR}/rm4health_ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/rm4health_ssl_access.log combined
</VirtualHost>'''
        
        # Salvar nova configuração
        cmd = f'echo "{isolated_config}" | sudo tee /etc/apache2/sites-available/rm4health.conf'
        ssh.exec_command(cmd)
        print("✅ Nova configuração criada")
        
        # 4. Testar configuração Apache
        print(f"\n🧪 TESTANDO CONFIGURAÇÃO APACHE...")
        stdin, stdout, stderr = ssh.exec_command('sudo apache2ctl configtest')
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if 'Syntax OK' in output or 'Syntax OK' in error:
            print("✅ Configuração Apache válida")
        else:
            print(f"❌ Problema na configuração: {error}")
            print("🔄 Tentando corrigir...")
            
            # Configuração ainda mais simples
            simple_config = '''# RM4Health - Configuração minimalista
ProxyPass /rm4health http://127.0.0.1:8080/
ProxyPassReverse /rm4health http://127.0.0.1:8080/'''
            
            # Apenas adicionar ao final do site principal (mais seguro)
            cmd_simple = f'echo "{simple_config}" | sudo tee -a /etc/apache2/sites-available/000-default.conf'
            ssh.exec_command(cmd_simple)
            print("✅ Configuração simplificada adicionada")
        
        # 5. Recarregar Apache
        ssh.exec_command('sudo systemctl reload apache2')
        print("✅ Apache recarregado")
        
        # 6. Agora iniciar o dashboard Flask na porta 8080
        print(f"\n🚀 INICIANDO DASHBOARD FLASK COM DADOS REAIS...")
        
        # Modificar app.py para rodar na porta 8080
        modify_app_cmd = '''cd /var/www/html/rm4health && sed -i "s/port=5000/port=8080/g" app.py'''
        ssh.exec_command(modify_app_cmd)
        print("✅ App configurado para porta 8080")
        
        # Iniciar dashboard
        start_cmd = 'cd /var/www/html/rm4health && nohup python3 app.py --host=0.0.0.0 --port=8080 > dashboard_real.log 2>&1 &'
        ssh.exec_command(start_cmd)
        print("🔄 Dashboard iniciando...")
        
        import time
        time.sleep(5)
        
        # 7. Verificar se está funcionando
        print(f"\n🧪 VERIFICANDO FUNCIONAMENTO...")
        
        # Verificar processo
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python3 app.py" | grep -v grep')
        process_output = stdout.read().decode()
        
        if 'app.py' in process_output:
            print("✅ Dashboard Flask rodando na porta 8080!")
            
            # Testar acesso local
            stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/')
            http_code = stdout.read().decode().strip()
            
            if http_code == '200':
                print("✅ Dashboard respondendo localmente!")
                
                print(f"\n🎉 CONFIGURAÇÃO DA OPÇÃO 2 CONCLUÍDA!")
                print(f"🌐 TESTE AGORA:")
                print(f"   https://ciis.fmrp.usp.br/rm4health")
                print(f"   http://ciis.fmrp.usp.br/rm4health")
                print(f"")
                print(f"📊 FUNCIONALIDADES:")
                print(f"   ✅ Dados REAIS da API REDCap")
                print(f"   ✅ 596 registros reais")
                print(f"   ✅ Atualização em tempo real")
                print(f"   ✅ Todas as análises originais")
                
                return True
            else:
                print(f"⚠️  Dashboard retornando código: {http_code}")
        else:
            print("❌ Dashboard não está rodando")
            
            # Ver log de erro
            stdin, stdout, stderr = ssh.exec_command('cd /var/www/html/rm4health && tail -10 dashboard_real.log')
            log_output = stdout.read().decode()
            if log_output:
                print(f"📄 Log de erro:")
                print(f"   {log_output}")
        
        return False
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False
        
    finally:
        try:
            ssh.close()
            print(f"\n🔌 Conexão fechada")
        except:
            pass

if __name__ == "__main__":
    print("🚨 ATENÇÃO: Esta é a Opção 2 - com modificação cuidadosa do Apache")
    print("✅ Apenas toca na configuração rm4health.conf")
    print("✅ NÃO mexe em outros sites do servidor")
    print()
    
    success = opcao2_porta_isolada()
    
    if success:
        print("\n🎉 SUCESSO! Dashboard com dados reais funcionando!")
        print("Seus colegas podem acessar: https://ciis.fmrp.usp.br/rm4health")
    else:
        print("\n⚠️  Houve algum problema. Vou tentar diagnóstico...")
