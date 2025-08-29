import pandas as pd
import os
import json
from datetime import datetime, timedelta
from redcap_client import REDCapClient
import traceback

class CSVDataManager:
    """Gerenciador de dados CSV com atualização via VPN"""
    
    def __init__(self, csv_file='redcap_data.csv', metadata_file='redcap_metadata.json'):
        self.csv_file = csv_file
        self.metadata_file = metadata_file
        self.redcap_client = REDCapClient()
        
    def get_data(self):
        """Retorna dados do CSV (prioridade) ou tenta atualizar via API"""
        try:
            # Tentar carregar CSV primeiro
            if os.path.exists(self.csv_file):
                print(f"📁 Carregando dados do CSV: {self.csv_file}")
                df = pd.read_csv(self.csv_file)
                data = df.to_dict('records')
                
                # Verificar idade dos dados
                csv_age = self.get_csv_age()
                print(f"📅 Dados CSV têm {csv_age} horas")
                
                # Tentar atualizar se dados estão velhos E VPN disponível
                if csv_age > 24:  # Mais de 24 horas
                    print("🔄 Dados antigos, tentando atualizar via VPN...")
                    self.try_update_from_redcap()
                
                return data
            else:
                print("❌ CSV não encontrado, tentando buscar via REDCap...")
                return self.try_update_from_redcap()
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return []
    
    def get_csv_age(self):
        """Retorna idade do CSV em horas"""
        try:
            if os.path.exists(self.csv_file):
                csv_time = datetime.fromtimestamp(os.path.getmtime(self.csv_file))
                age_hours = (datetime.now() - csv_time).total_seconds() / 3600
                return age_hours
            return float('inf')
        except:
            return float('inf')
    
    def try_update_from_redcap(self):
        """Tenta atualizar dados via REDCap (VPN necessária)"""
        try:
            print("🔌 Testando conexão REDCap...")
            if self.redcap_client.test_connection():
                print("✅ VPN disponível! Atualizando dados...")
                
                # Buscar dados
                data = self.redcap_client.get_records()
                if data and len(data) > 0:
                    # Salvar em CSV
                    df = pd.DataFrame(data)
                    df.to_csv(self.csv_file, index=False, encoding='utf-8')
                    print(f"💾 Dados salvos em CSV: {len(data)} registros")
                    
                    # Salvar metadados
                    try:
                        project_info = self.redcap_client.get_project_info()
                        metadata = {
                            'last_update': datetime.now().isoformat(),
                            'records_count': len(data),
                            'project_info': project_info,
                            'source': 'redcap_api'
                        }
                        with open(self.metadata_file, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, indent=2, ensure_ascii=False)
                        print("📋 Metadados salvos")
                    except Exception as e:
                        print(f"⚠️ Erro nos metadados: {e}")
                    
                    return data
                else:
                    print("❌ Nenhum dado retornado do REDCap")
                    return self.load_csv_fallback()
            else:
                print("❌ REDCap indisponível (sem VPN)")
                return self.load_csv_fallback()
                
        except Exception as e:
            print(f"❌ Erro na atualização REDCap: {e}")
            traceback.print_exc()
            return self.load_csv_fallback()
    
    def load_csv_fallback(self):
        """Carrega CSV como fallback"""
        try:
            if os.path.exists(self.csv_file):
                print("📁 Usando CSV existente como fallback")
                df = pd.read_csv(self.csv_file)
                return df.to_dict('records')
            else:
                print("❌ Nenhum CSV disponível")
                return []
        except Exception as e:
            print(f"❌ Erro no fallback CSV: {e}")
            return []
    
    def force_update(self):
        """Força atualização via REDCap (para usar manualmente via VPN)"""
        print("🔄 FORÇANDO atualização via REDCap...")
        return self.try_update_from_redcap()
    
    def get_metadata(self):
        """Retorna metadados dos dados"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    def get_data_status(self):
        """Retorna status dos dados"""
        metadata = self.get_metadata()
        csv_exists = os.path.exists(self.csv_file)
        csv_age = self.get_csv_age()
        
        status = {
            'csv_exists': csv_exists,
            'csv_age_hours': csv_age,
            'last_update': metadata.get('last_update', 'Desconhecido'),
            'records_count': metadata.get('records_count', 0),
            'is_recent': csv_age < 24,
            'source': metadata.get('source', 'unknown'),
            'redcap_available': False
        }
        
        # Testar REDCap rapidamente
        try:
            status['redcap_available'] = self.redcap_client.test_connection()
        except:
            pass
            
        return status
