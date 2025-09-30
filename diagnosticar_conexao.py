#!/usr/bin/env python3
import paramiko

def diagnosticar_conexao_recusada():
    print("🔍 DIAGNÓSTICO: ERR_CONNECTION_REFUSED")
    print("🎯 Verificando URL, Apache, portas e conectividade")
    print("-" * 60)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')
        
        diagnosticos = [
            # 1. Verificar se Apache está rodando
            ('systemctl status apache2 --no-pager', 'Status do Apache'),
            
            # 2. Verificar portas abertas
            ('ss -tlnp | grep :80', 'Porta 80 (HTTP)'),
            ('ss -tlnp | grep :443', 'Porta 443 (HTTPS)'),
            ('ss -tlnp | grep :8080', 'Porta 8080 (Dashboard)'),
            
            # 3. Verificar se dashboard está rodando
            ('ps aux | grep "python3 app.py" | grep -v grep', 'Processo Dashboard'),
            
            # 4. Testar conectividade local
            ('curl -I http://127.0.0.1/', 'Teste Apache local'),
            ('curl -I http://127.0.0.1:8080/', 'Teste Dashboard local'),
            
            # 5. Verificar configuração DNS/domínio
            ('nslookup ciis.fmrp.usp.br', 'Resolução DNS'),
            
            # 6. Verificar logs recentes
            ('tail -5 /var/log/apache2/error.log', 'Erros Apache'),
            ('tail -5 /var/log/apache2/access.log', 'Acessos Apache'),
            
            # 7. Verificar configurações sites
            ('apache2ctl -S', 'Sites Apache ativos'),
        ]
        
        for cmd, desc in diagnosticos:
            print(f"\n🔄 {desc}...")
            try:
                stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                
                if output:
                    print(f"✅ {desc}:")
                    print(f"   📄 {output[:400]}{'...' if len(output) > 400 else ''}")
                elif error:
                    print(f"⚠️  {desc} - Error:")
                    print(f"   ❌ {error[:200]}{'...' if len(error) > 200 else ''}")
                else:
                    print(f"⚪ {desc} - Sem output")
                    
            except Exception as e:
                print(f"❌ {desc} - Timeout/Erro: {str(e)[:100]}")
        
        # Teste específico da URL
        print(f"\n🌐 TESTANDO URLs ESPECÍFICAS...")
        
        test_urls = [
            'http://ciis.fmrp.usp.br',
            'https://ciis.fmrp.usp.br', 
            'http://ciis.fmrp.usp.br/rm4health',
            'https://ciis.fmrp.usp.br/rm4health'
        ]
        
        for url in test_urls:
            try:
                cmd = f'curl -I -m 10 "{url}"'
                stdin, stdout, stderr = ssh.exec_command(cmd)
                output = stdout.read().decode().strip()
                
                if '200 OK' in output:
                    print(f"✅ {url} - OK")
                elif '404' in output:
                    print(f"⚠️  {url} - 404 Not Found")
                elif '502' in output:
                    print(f"❌ {url} - 502 Bad Gateway")
                else:
                    print(f"⚠️  {url} - {output.split()[0] if output else 'No response'}")
                    
            except:
                print(f"❌ {url} - Timeout/Connection failed")
        
        print(f"\n🔧 POSSÍVEIS SOLUÇÕES:")
        print(f"1️⃣  Apache parado → sudo systemctl start apache2")
        print(f"2️⃣  Firewall bloqueando → sudo ufw allow 80,443")
        print(f"3️⃣  Configuração proxy incorreta → corrigir rm4health.conf")
        print(f"4️⃣  Dashboard não rodando → reiniciar Flask")
        print(f"5️⃣  DNS/SSL issues → verificar certificados")
        
    except Exception as e:
        print(f"❌ ERRO DE CONEXÃO: {str(e)}")
        print(f"💡 Possíveis causas:")
        print(f"   - Servidor está offline")
        print(f"   - Firewall bloqueando SSH")
        print(f"   - Credenciais alteradas")
        
    finally:
        try:
            ssh.close()
            print(f"\n🔌 Diagnóstico concluído")
        except:
            pass

if __name__ == "__main__":
    print("🚨 ERRO: ciis.fmrp.usp.br recusou conexão")
    print("Vamos descobrir exatamente o que está acontecendo...")
    print()
    diagnosticar_conexao_recusada()
