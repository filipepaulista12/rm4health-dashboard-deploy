#!/usr/bin/env python3
import paramiko

def corrigir_e_testar():
    hostname = '200.144.254.4'
    port = 22
    username = 'ubuntu' 
    password = 'vFpyJS4FA'
    
    print("🔧 CORRIGINDO CONFIGURAÇÃO E TESTANDO")
    print("-" * 50)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("🔌 Conectando...")
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # Lista de comandos para corrigir
        comandos = [
            # Instalar pip corretamente
            ('sudo apt install python3-pip python3-venv -y', 'Instalando pip e venv'),
            
            # Limpar venv anterior e recriar
            ('rm -rf /var/www/html/rm4health/venv', 'Removendo venv anterior'),
            ('cd /var/www/html/rm4health && python3 -m venv venv', 'Criando novo venv'),
            
            # Verificar se venv foi criado
            ('ls -la /var/www/html/rm4health/venv/', 'Verificando venv'),
            
            # Instalar dependências globalmente primeiro (fallback)
            ('pip3 install flask plotly pandas requests gunicorn', 'Instalando deps globalmente'),
            
            # Tentar no venv novamente
            ('cd /var/www/html/rm4health && source venv/bin/activate && pip install flask plotly pandas requests gunicorn', 'Instalando no venv'),
            
            # Testar app diretamente com python global
            ('cd /var/www/html/rm4health && python3 -c "import flask; print(\'Flask OK\')"', 'Testando Flask'),
            
            # Criar versão mais simples do start.sh
            ('echo "#!/bin/bash\ncd /var/www/html/rm4health\npython3 app.py" > /var/www/html/rm4health/start_global.sh', 'Criando start global'),
            ('chmod +x /var/www/html/rm4health/start_global.sh', 'Permissão start global'),
        ]
        
        for cmd, desc in comandos:
            print(f"\n🔄 {desc}...")
            try:
                stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
                exit_code = stdout.channel.recv_exit_status()
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                
                if exit_code == 0:
                    print(f"✅ {desc} - OK")
                    if output and len(output) < 200:
                        print(f"   📄 {output}")
                else:
                    print(f"⚠️  {desc} - Warning (exit: {exit_code})")
                    if error:
                        print(f"   ❌ {error[:200]}")
                        
            except Exception as e:
                print(f"❌ {desc} - Erro: {str(e)[:100]}")
            
        # Teste final da aplicação
        print("\n🧪 TESTE FINAL DA APLICAÇÃO:")
        cmd_final = 'cd /var/www/html/rm4health && python3 -c "from app import app; print(\'✓ Dashboard pronto para usar!\')"'
        
        try:
            stdin, stdout, stderr = ssh.exec_command(cmd_final, timeout=30)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            if "Dashboard pronto" in output:
                print("🎉 SUCESSO! Dashboard funcionando!")
            else:
                print(f"❌ Erro no teste final: {error}")
                
        except Exception as e:
            print(f"⚠️  Teste final com timeout: {str(e)}")
            
        print(f"\n🌐 DASHBOARD DISPONÍVEL EM:")
        print(f"   https://ciis.fmrp.usp.br/rm4health/")
        print(f"\n🚀 PARA INICIAR MANUALMENTE:")
        print(f"   ssh ubuntu@200.144.254.4")
        print(f"   cd /var/www/html/rm4health") 
        print(f"   ./start_global.sh")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {str(e)}")
        
    finally:
        try:
            ssh.close()
            print("\n🔌 Conexão fechada")
        except:
            pass

if __name__ == "__main__":
    corrigir_e_testar()
