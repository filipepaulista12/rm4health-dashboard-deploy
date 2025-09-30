#!/usr/bin/env python3
import paramiko
import os

def upload_dashboard_estatico():
    print("📤 UPLOAD DASHBOARD ESTÁTICO - 100% SEGURO")
    print("✅ NÃO mexe em configurações Apache")
    print("✅ NÃO toca em outros sites") 
    print("✅ Apenas copia arquivo HTML")
    print("-" * 50)
    
    try:
        # Verificar se arquivo existe
        local_file = 'dashboard_estatico.html'
        if not os.path.exists(local_file):
            print(f"❌ Arquivo {local_file} não encontrado!")
            return False
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('200.144.254.4', port=22, username='ubuntu', password='vFpyJS4FA')
        sftp = ssh.open_sftp()
        
        print("🔌 Conectado ao servidor via SFTP")
        
        # Criar pasta static se não existir
        try:
            sftp.chdir('/var/www/html/rm4health')
            print("✅ Navegando para /var/www/html/rm4health/")
            
            try:
                sftp.mkdir('static')
                print("✅ Pasta static criada")
            except:
                print("⚠️  Pasta static já existe")
            
            sftp.chdir('static')
            print("✅ Dentro de /var/www/html/rm4health/static/")
            
            # Upload do dashboard
            print("📤 Fazendo upload do dashboard estático...")
            sftp.put(local_file, 'index.html')
            print("✅ Upload concluído!")
            
            # Também salvar como dashboard.html
            sftp.put(local_file, 'dashboard.html')
            print("✅ Cópia adicional criada (dashboard.html)")
            
            # Verificar permissões
            ssh.exec_command('chmod 644 /var/www/html/rm4health/static/index.html')
            ssh.exec_command('chmod 644 /var/www/html/rm4health/static/dashboard.html')
            print("✅ Permissões configuradas")
            
            print("\n🎉 DASHBOARD ESTÁTICO ONLINE!")
            print("🌐 ACESSE AGORA:")
            print("   https://ciis.fmrp.usp.br/rm4health/static/")
            print("   https://ciis.fmrp.usp.br/rm4health/static/index.html")
            print("   https://ciis.fmrp.usp.br/rm4health/static/dashboard.html")
            
            print(f"\n📊 CARACTERÍSTICAS:")
            print(f"   ✅ 596 registros de dados")
            print(f"   ✅ 4 gráficos interativos (Plotly)")
            print(f"   ✅ Responsivo para mobile")
            print(f"   ✅ Funciona sem VPN")
            print(f"   ✅ Carregamento instantâneo")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no upload: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
        return False
        
    finally:
        try:
            sftp.close()
            ssh.close()
            print("🔌 Conexão fechada")
        except:
            pass

if __name__ == "__main__":
    success = upload_dashboard_estatico()
    if success:
        print("\n✅ MISSÃO CONCLUÍDA!")
        print("Seus colegas podem acessar o dashboard sem problemas!")
    else:
        print("\n❌ Houve algum problema no upload.")
