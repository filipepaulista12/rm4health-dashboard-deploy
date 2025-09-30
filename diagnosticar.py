#!/usr/bin/env python3
import paramiko

def diagnosticar_problema():
    print("🔍 DIAGNÓSTICO COMPLETO DO PROBLEMA")
    print("-" * 50)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')
        
        diagnosticos = [
            # Verificar se o dashboard está rodando
            ('ps aux | grep "python3 app.py"', 'Processos Python rodando'),
            ('netstat -tlnp | grep 8000', 'Porta 8000 em uso'),
            
            # Verificar logs do dashboard
            ('cd /var/www/html/rm4health && ls -la dashboard.log', 'Log do dashboard'),
            ('cd /var/www/html/rm4health && tail -20 dashboard.log', 'Últimas linhas do log'),
            
            # Verificar configuração Apache
            ('apache2ctl configtest', 'Configuração Apache'),
            ('systemctl status apache2', 'Status do Apache'),
            ('ls -la /etc/apache2/sites-enabled/', 'Sites habilitados'),
            
            # Verificar logs do Apache
            ('tail -10 /var/log/apache2/error.log', 'Erros Apache'),
            ('tail -10 /var/log/apache2/access.log', 'Acessos Apache'),
            
            # Testar conexão local
            ('curl -I http://127.0.0.1:8000/', 'Teste local porta 8000'),
        ]
        
        for cmd, desc in diagnosticos:
            print(f"\n🔄 {desc}...")
            try:
                stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                
                if output:
                    print(f"✅ {desc}:")
                    print(f"   📄 {output[:500]}{'...' if len(output) > 500 else ''}")
                elif error:
                    print(f"⚠️  {desc} - Error:")
                    print(f"   ❌ {error[:300]}{'...' if len(error) > 300 else ''}")
                else:
                    print(f"⚪ {desc} - Sem output")
                    
            except Exception as e:
                print(f"❌ {desc} - Exceção: {str(e)[:100]}")
        
        # Tentar reiniciar o dashboard
        print(f"\n🔄 TENTANDO REINICIAR DASHBOARD...")
        
        # Matar processos
        ssh.exec_command('pkill -f "python3 app.py"')
        print("🔄 Parando processos anteriores...")
        
        import time
        time.sleep(2)
        
        # Iniciar novamente
        start_cmd = 'cd /var/www/html/rm4health && nohup python3 app.py --host=0.0.0.0 --port=8000 > dashboard.log 2>&1 &'
        ssh.exec_command(start_cmd)
        print("🔄 Reiniciando dashboard...")
        
        time.sleep(3)
        
        # Verificar se iniciou
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python3 app.py" | grep -v grep')
        output = stdout.read().decode().strip()
        
        if output:
            print("✅ Dashboard reiniciado com sucesso!")
            print(f"   📄 {output}")
            
            # Testar acesso local
            stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/')
            http_code = stdout.read().decode().strip()
            
            if http_code == '200':
                print("✅ Dashboard respondendo localmente!")
            else:
                print(f"⚠️  Dashboard retornando código: {http_code}")
                
        else:
            print("❌ Dashboard não conseguiu iniciar!")
            
            # Verificar erro no log
            stdin, stdout, stderr = ssh.exec_command('cd /var/www/html/rm4health && tail -10 dashboard.log')
            log_output = stdout.read().decode().strip()
            if log_output:
                print(f"📄 Últimas linhas do log:")
                print(f"   {log_output}")
        
        print(f"\n📋 PRÓXIMOS PASSOS:")
        print(f"1. Se o dashboard não estiver rodando, há erro no código")
        print(f"2. Se estiver rodando mas não acessível, é problema de proxy")
        print(f"3. Verifique: https://ciis.fmrp.usp.br/rm4health/")
        
    except Exception as e:
        print(f"❌ ERRO NO DIAGNÓSTICO: {str(e)}")
        
    finally:
        try:
            ssh.close()
            print(f"\n🔌 Diagnóstico concluído")
        except:
            pass

if __name__ == "__main__":
    diagnosticar_problema()
