from local_redcap_client import LocalREDCapClient

def debug_participants():
    client = LocalREDCapClient()
    data = client.get_records()
    
    print(f"Total de registros: {len(data)}")
    
    # Pegar o primeiro registro para analisar
    if data:
        sample = data[0]
        complete_fields = [k for k in sample.keys() if k.endswith('_complete')]
        print(f"Campos _complete encontrados: {len(complete_fields)}")
        print("Primeiros 10 campos _complete:", complete_fields[:10])
        
        # Mostrar alguns valores de exemplo
        print("\nExemplos de valores:")
        for field in complete_fields[:5]:
            values = []
            for record in data[:5]:
                value = record.get(field)
                if value is not None and str(value).strip() != '':
                    values.append(value)
            if values:
                print(f"{field}: {values}")
    
    # Testar a lógica do participante
    participant_records = {}
    for record in data[:20]:  # Primeiros 20 registros
        participant_id = None
        for id_field in ['participant_code', 'record_id', 'participant_code_estudo']:
            if id_field in record and record[id_field]:
                participant_id = record[id_field]
                break
        
        if participant_id:
            if participant_id not in participant_records:
                participant_records[participant_id] = []
            participant_records[participant_id].append(record)
    
    print(f"\nParticipantes encontrados: {len(participant_records)}")
    
    # Analisar primeiro participante
    if participant_records:
        first_participant = list(participant_records.keys())[0]
        records = participant_records[first_participant]
        
        print(f"\n=== PARTICIPANTE {first_participant} ===")
        print(f"Registros: {len(records)}")
        
        forms_status = {}
        for record in records:
            for field_name, value in record.items():
                if field_name.endswith('_complete') and value is not None and str(value).strip() != '':
                    form_name = field_name.replace('_complete', '')
                    current_status = str(value).strip()
                    
                    if form_name not in forms_status or int(current_status) > int(forms_status.get(form_name, '0')):
                        forms_status[form_name] = current_status
        
        print(f"Formulários encontrados: {len(forms_status)}")
        
        complete_forms = sum(1 for status in forms_status.values() if status == '2')
        incomplete_forms = sum(1 for status in forms_status.values() if status == '1')
        unverified_forms = sum(1 for status in forms_status.values() if status == '0')
        
        print(f"Completos: {complete_forms}")
        print(f"Incompletos: {incomplete_forms}")
        print(f"Não verificados: {unverified_forms}")
        print(f"Total: {complete_forms + incomplete_forms + unverified_forms}")

if __name__ == "__main__":
    debug_participants()
