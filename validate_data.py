#!/usr/bin/env python3
"""Script para validar os dados reais e verificar campos"""

from local_redcap_client import LocalREDCapClient
from data_processor import DataProcessor

def main():
    print("=== VALIDAÇÃO DOS DADOS REAIS ===")
    
    # Carregar cliente
    client = LocalREDCapClient()
    
    # Examinar dados brutos
    records = client.get_records(raw_or_label='raw')
    print(f"\n📊 Total de registros: {len(records)}")
    
    if records:
        first_record = records[0]
        all_fields = list(first_record.keys())
        
        print(f"📋 Total de campos: {len(all_fields)}")
        
        # Campos de identificação
        id_fields = [f for f in all_fields if any(word in f.lower() for word in ['participant', 'id', 'record'])]
        print(f"\n🆔 Campos de identificação: {id_fields[:5]}")
        
        # Campos demográficos
        demo_fields = [f for f in all_fields if any(word in f.lower() for word in ['age', 'birth', 'sex', 'gender', 'group'])]
        print(f"👥 Campos demográficos: {demo_fields}")
        
        # Campos de instrumentos (complete)
        instr_fields = [f for f in all_fields if 'complete' in f.lower()]
        print(f"📝 Instrumentos (campos *_complete): {len(instr_fields)}")
        print(f"    Primeiros 5: {instr_fields[:5]}")
        
        # Testar DataProcessor
        print(f"\n=== TESTANDO DATA PROCESSOR ===")
        dp = DataProcessor(records)  # Passar records, não client
        
        # Estatísticas básicas
        basic_stats = dp.get_basic_stats()
        print(f"📈 Estatísticas básicas:")
        for key, value in basic_stats.items():
            print(f"    {key}: {value}")
        
        # Demografia
        print(f"\n👥 Demografia:")
        age_dist = dp.get_age_distribution()
        gender_dist = dp.get_gender_distribution()
        print(f"    Distribuição de idade: {age_dist}")
        print(f"    Distribuição de género: {gender_dist}")
        
        # Examinar valores específicos
        print(f"\n=== VALORES DE EXEMPLO ===")
        print(f"participant_code: {first_record.get('participant_code', 'N/A')}")
        print(f"participant_group: {first_record.get('participant_group', 'N/A')}")
        print(f"birth_year: {first_record.get('birth_year', 'N/A')}")
        print(f"sex: {first_record.get('sex', 'N/A')}")

if __name__ == "__main__":
    main()