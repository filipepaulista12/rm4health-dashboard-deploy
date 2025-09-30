#!/usr/bin/env python3
"""
Verificar campos de identificação nos dados RM4Health
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from redcap_client import REDCapClient

def check_id_fields():
    """Verifica campos de identificação"""
    
    print("🔍 INVESTIGANDO CAMPOS DE IDENTIFICAÇÃO")
    print("=" * 50)
    
    try:
        redcap = REDCapClient()
        data = redcap.get_records()
        print(f"✅ {len(data)} registros obtidos")
        print()
        
        if data:
            sample = data[0]
            print("🆔 POSSÍVEIS CAMPOS DE IDENTIFICAÇÃO:")
            
            id_keywords = ['id', 'participant', 'subject', 'patient', 'code']
            
            for field in sample.keys():
                field_lower = field.lower()
                for keyword in id_keywords:
                    if keyword in field_lower:
                        # Mostrar valores únicos
                        values = set()
                        for record in data[:20]:
                            if field in record and record[field]:
                                values.add(str(record[field]))
                        
                        print(f"  📋 {field}:")
                        if values:
                            print(f"    Valores únicos (amostra): {list(values)[:5]}")
                            print(f"    Total valores únicos: {len(set(str(r.get(field, '')) for r in data if r.get(field)))}")
                        print()
                        break
            
            # Mostrar estrutura do primeiro registro
            print("📊 ESTRUTURA DO PRIMEIRO REGISTRO:")
            print("-" * 40)
            for i, (key, value) in enumerate(sample.items()):
                if i < 15:  # Primeiros 15 campos
                    print(f"  {key}: {value}")
                else:
                    print(f"  ... e mais {len(sample) - 15} campos")
                    break
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_id_fields()
