#!/usr/bin/env python3
"""Script para validar página de participantes"""

from local_redcap_client import LocalREDCapClient
from data_processor import DataProcessor

def validate_participants_page():
    print("=== VALIDAÇÃO PÁGINA PARTICIPANTES ===")
    
    # Carregar dados
    client = LocalREDCapClient()
    records = client.get_records(raw_or_label='raw')
    
    print(f"📊 Total registros: {len(records)}")
    
    # Simular lógica da página de participantes
    participants_data = []
    participant_records = {}
    
    # Agrupa registros por participante (mesma lógica do app.py)
    for record in records:
        participant_id = None
        for id_field in ['participant_code', 'record_id', 'participant_code_estudo']:
            if id_field in record and record[id_field]:
                participant_id = record[id_field]
                break
                
        if participant_id:
            if participant_id not in participant_records:
                participant_records[participant_id] = []
            participant_records[participant_id].append(record)
    
    print(f"👥 Participantes únicos identificados: {len(participant_records)}")
    
    # Examinar alguns participantes
    total_complete = 0
    total_incomplete = 0
    total_unverified = 0
    
    for i, (participant_id, records) in enumerate(list(participant_records.items())[:5]):
        forms_status = {}
        
        for record in records:
            for field_name, value in record.items():
                if field_name.endswith('_complete') and value is not None and str(value).strip() != '':
                    form_name = field_name.replace('_complete', '')
                    current_status = str(value).strip()
                    
                    # Mapear status
                    if current_status in ['2', 'complete', 'completed']:
                        current_status = '2'
                    elif current_status in ['1', 'incomplete', 'partial']:
                        current_status = '1'
                    else:
                        current_status = '0'
                    
                    if form_name not in forms_status or int(current_status) > int(forms_status.get(form_name, '0')):
                        forms_status[form_name] = current_status
        
        # Contar status
        complete_forms = sum(1 for status in forms_status.values() if status == '2')
        incomplete_forms = sum(1 for status in forms_status.values() if status == '1')
        unverified_forms = sum(1 for status in forms_status.values() if status == '0')
        
        total_complete += complete_forms
        total_incomplete += incomplete_forms
        total_unverified += unverified_forms
        
        completion_rate = round((complete_forms / (complete_forms + incomplete_forms)) * 100, 1) if (complete_forms + incomplete_forms) > 0 else 0
        
        if i < 3:  # Mostrar apenas os primeiros 3
            print(f"  Participante {participant_id}: {len(records)} registros, {complete_forms}C/{incomplete_forms}I/{unverified_forms}U, {completion_rate}%")
    
    print(f"\n📈 TOTAIS CALCULADOS:")
    print(f"  Formulários completos: {total_complete}")
    print(f"  Formulários incompletos: {total_incomplete}")
    print(f"  Formulários não verificados: {total_unverified}")
    
    # Verificar campos _complete disponíveis
    complete_fields = set()
    for record in records[:10]:  # Examinar os primeiros 10 registros
        for field_name in record.keys():
            if field_name.endswith('_complete'):
                complete_fields.add(field_name)
    
    print(f"\n📝 Campos _complete disponíveis ({len(complete_fields)}):")
    for field in sorted(complete_fields):
        print(f"  - {field}")

if __name__ == "__main__":
    validate_participants_page()