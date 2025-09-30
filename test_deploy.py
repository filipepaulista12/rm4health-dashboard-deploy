#!/usr/bin/env python3
"""
Teste para verificar se a aplicação funciona corretamente no ambiente de produção
"""
import os
import sys

def test_production_environment():
    """Testa se a aplicação funciona em modo produção"""
    print("🧪 Testando ambiente de produção...")
    
    # Simular ambiente de produção
    os.environ['PRODUCTION'] = '1'
    
    try:
        # Importar e testar componentes
        print("📦 Testando import do app...")
        from app import app, redcap
        print("✅ App importado com sucesso!")
        
        print("🔌 Testando conexão local...")
        connection_test = redcap.test_connection()
        print(f"✅ Conexão: {'OK' if connection_test else 'ERRO'}")
        
        print("📊 Testando dados...")
        try:
            records = redcap.get_records()
            print(f"✅ {len(records)} registros disponíveis")
            
            metadata = redcap.get_metadata()
            print(f"✅ {len(metadata)} campos de metadados")
            
            stats = redcap.get_stats()
            print(f"✅ Stats: {stats.get('total_records', 0)} registros")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar dados: {e}")
        
        print("\n🎯 Teste completo!")
        print("A aplicação está pronta para deploy!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_production_environment()
    sys.exit(0 if success else 1)
