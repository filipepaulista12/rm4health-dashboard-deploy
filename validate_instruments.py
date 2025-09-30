#!/usr/bin/env python3
"""Script para validar análise detalhada dos 11 instrumentos com explicações para leigos"""

from local_redcap_client import LocalREDCapClient
from data_processor import DataProcessor

def validate_instruments_analysis():
    print("=== VALIDAÇÃO ANÁLISE DETALHADA DOS INSTRUMENTOS ===")
    print("Analisando os 11 questionários/escalas clínicas usados no RM4Health\n")
    
    # Carregar dados
    client = LocalREDCapClient()
    data = client.get_records(raw_or_label='raw')
    
    if not data:
        print("❌ Dados não disponíveis")
        return
    
    dp = DataProcessor(data)
    print(f"📊 Analisando {len(data)} registos de dados...\n")
    
    # 1. IDENTIFICAR INSTRUMENTOS PELOS CAMPOS _complete
    print("🔍 1. IDENTIFICAÇÃO DOS INSTRUMENTOS")
    print("   O que são: Questionários e escalas validadas para avaliar diferentes aspetos da saúde")
    
    complete_fields = []
    for record in data[:10]:  # Examinar primeiros 10 registos
        for field_name in record.keys():
            if field_name.endswith('_complete'):
                complete_fields.append(field_name)
    
    # Remover duplicados e contar
    unique_instruments = list(set(complete_fields))
    
    print(f"\n   Instrumentos encontrados ({len(unique_instruments)}):")
    instrument_names = {}
    for i, field in enumerate(sorted(unique_instruments), 1):
        instrument_name = field.replace('_complete', '').replace('_', ' ').title()
        instrument_names[field] = instrument_name
        print(f"   {i}. {instrument_name}")
        
        # Explicação para leigos de cada instrumento
        if 'barthel' in field.lower():
            print(f"      → Avalia independência nas atividades básicas (comer, vestir, caminhar)")
        elif 'eq5d' in field.lower():
            print(f"      → Mede qualidade de vida em 5 dimensões (mobilidade, cuidados pessoais, etc.)")
        elif 'pittsburgh' in field.lower() or 'sono' in field.lower():
            print(f"      → Avalia qualidade do sono e problemas de insónia")
        elif 'caracterizacao' in field.lower():
            print(f"      → Recolhe dados socioeconómicos (educação, rendimento, habitação)")
        elif 'preferencias' in field.lower():
            print(f"      → Avalia hábitos, rotinas e preferências de atividades")
        elif 'medicacao' in field.lower():
            print(f"      → Monitoriza adesão aos medicamentos e bem-estar")
        elif 'utilizacao' in field.lower() and 'servicos' in field.lower():
            print(f"      → Regista uso de serviços de saúde (consultas, emergências, hospitalizações)")
        elif 'tecnologias' in field.lower():
            print(f"      → Avalia familiaridade e uso de tecnologias de saúde")
        elif 'plano' in field.lower() and 'terapeutico' in field.lower():
            print(f"      → Regista plano de medicamentos prescritos")
        elif 'estado' in field.lower() and 'saude' in field.lower():
            print(f"      → Lista diagnósticos e condições de saúde prévias")
        elif 'participante' in field.lower():
            print(f"      → Dados básicos do participante (identificação, grupo)")
    
    print()
    
    # 2. CALCULAR TAXAS DE COMPLETUDE POR INSTRUMENTO
    print("📈 2. TAXAS DE COMPLETUDE POR INSTRUMENTO")
    print("   O que significa: Percentagem de participantes que completaram cada questionário")
    
    total_records = len(data)
    instrument_completeness = {}
    
    for field in unique_instruments:
        completed_count = 0
        incomplete_count = 0
        not_started_count = 0
        
        for record in data:
            value = record.get(field, '')
            if str(value).strip() in ['2', 'complete', 'completed']:
                completed_count += 1
            elif str(value).strip() in ['1', 'incomplete', 'partial']:
                incomplete_count += 1
            else:
                not_started_count += 1
        
        completion_rate = (completed_count / total_records * 100) if total_records > 0 else 0
        instrument_completeness[field] = {
            'completed': completed_count,
            'incomplete': incomplete_count,
            'not_started': not_started_count,
            'completion_rate': completion_rate
        }
        
        print(f"\n   📋 {instrument_names[field]}:")
        print(f"      • Completos: {completed_count} ({completion_rate:.1f}%)")
        print(f"      • Incompletos: {incomplete_count}")
        print(f"      • Não iniciados: {not_started_count}")
        
        # Interpretação para leigos
        if completion_rate >= 90:
            interpretation = "Excelente adesão! Quase todos os participantes completaram."
        elif completion_rate >= 75:
            interpretation = "Boa adesão! A maioria dos participantes completou."
        elif completion_rate >= 50:
            interpretation = "Adesão moderada. Metade dos participantes completou."
        else:
            interpretation = "Baixa adesão. Poucos participantes completaram."
        
        print(f"      💡 Para leigos: {interpretation}")
    
    print()
    
    # 3. DISTRIBUIÇÃO POR PARTICIPANTE
    print("👥 3. DISTRIBUIÇÃO POR PARTICIPANTE")
    print("   O que significa: Quantos questionários cada participante completou")
    
    # Agregar por participante
    participant_completions = {}
    for record in data:
        participant_id = record.get('participant_code', record.get('record_id', 'unknown'))
        
        if participant_id not in participant_completions:
            participant_completions[participant_id] = {
                'completed': 0,
                'total_instruments': len(unique_instruments)
            }
        
        # Contar instrumentos completos para este participante
        for field in unique_instruments:
            value = record.get(field, '')
            if str(value).strip() in ['2', 'complete', 'completed']:
                participant_completions[participant_id]['completed'] += 1
                break  # Evitar contar o mesmo instrumento múltiplas vezes
    
    # Calcular estatísticas de distribuição
    completion_counts = [p['completed'] for p in participant_completions.values()]
    avg_completion = sum(completion_counts) / len(completion_counts) if completion_counts else 0
    min_completion = min(completion_counts) if completion_counts else 0
    max_completion = max(completion_counts) if completion_counts else 0
    
    # Distribuição por faixas
    distribution = {
        'all_completed': len([c for c in completion_counts if c == len(unique_instruments)]),
        'mostly_completed': len([c for c in completion_counts if c >= len(unique_instruments) * 0.8 and c < len(unique_instruments)]),
        'partially_completed': len([c for c in completion_counts if c >= len(unique_instruments) * 0.5 and c < len(unique_instruments) * 0.8]),
        'few_completed': len([c for c in completion_counts if c < len(unique_instruments) * 0.5])
    }
    
    print(f"\n   📊 Estatísticas de completude por participante:")
    print(f"      • Média de instrumentos completados: {avg_completion:.1f}/{len(unique_instruments)}")
    print(f"      • Mínimo: {min_completion} instrumentos")
    print(f"      • Máximo: {max_completion} instrumentos")
    
    print(f"\n   📈 Distribuição dos participantes:")
    total_participants = len(participant_completions)
    print(f"      • Completaram tudo ({len(unique_instruments)}/{len(unique_instruments)}): {distribution['all_completed']} participantes ({distribution['all_completed']/total_participants*100:.1f}%)")
    print(f"      • Completaram quase tudo (≥80%): {distribution['mostly_completed']} participantes ({distribution['mostly_completed']/total_participants*100:.1f}%)")
    print(f"      • Completaram metade (50-80%): {distribution['partially_completed']} participantes ({distribution['partially_completed']/total_participants*100:.1f}%)")
    print(f"      • Completaram pouco (<50%): {distribution['few_completed']} participantes ({distribution['few_completed']/total_participants*100:.1f}%)")
    
    print(f"\n   💡 Para leigos:")
    if distribution['all_completed'] / total_participants >= 0.8:
        print("      Excelente! A maioria dos participantes completou todos os questionários.")
    elif distribution['all_completed'] / total_participants >= 0.6:
        print("      Muito bom! A maioria dos participantes teve alta completude.")
    elif distribution['all_completed'] / total_participants >= 0.4:
        print("      Razoável! Cerca de metade dos participantes completou bem os questionários.")
    else:
        print("      Precisa melhorar! Muitos participantes não completaram os questionários.")
    
    print()
    
    # 4. VALIDAÇÃO DE DADOS POR INSTRUMENTO
    print("🔍 4. VALIDAÇÃO DE DADOS POR INSTRUMENTO")
    print("   O que significa: Verificar se os dados coletados fazem sentido e são válidos")
    
    # Para cada instrumento, verificar campos relacionados
    validation_results = {}
    
    for field in unique_instruments:
        instrument_base = field.replace('_complete', '')
        
        # Procurar campos relacionados a este instrumento
        related_fields = []
        for record in data[:1]:  # Usar primeiro registo para examinar estrutura
            for field_name in record.keys():
                if instrument_base in field_name and field_name != field:
                    related_fields.append(field_name)
        
        # Calcular estatísticas de preenchimento dos campos relacionados
        if related_fields:
            total_possible = len(data) * len(related_fields)
            filled_fields = 0
            
            for record in data:
                for related_field in related_fields:
                    value = record.get(related_field, '')
                    if value is not None and str(value).strip() != '':
                        filled_fields += 1
            
            data_quality = (filled_fields / total_possible * 100) if total_possible > 0 else 0
        else:
            data_quality = 0
        
        validation_results[field] = {
            'related_fields_count': len(related_fields),
            'data_quality': data_quality
        }
        
        print(f"\n   📋 {instrument_names[field]}:")
        print(f"      • Campos de dados: {len(related_fields)}")
        print(f"      • Qualidade dos dados: {data_quality:.1f}%")
        
        # Interpretação para leigos
        if data_quality >= 90:
            quality_interpretation = "Dados excelentes! Quase todos os campos estão preenchidos."
        elif data_quality >= 75:
            quality_interpretation = "Dados bons! A maioria dos campos está preenchida."
        elif data_quality >= 50:
            quality_interpretation = "Dados razoáveis! Metade dos campos está preenchida."
        else:
            quality_interpretation = "Dados insuficientes! Muitos campos estão vazios."
        
        print(f"      💡 Para leigos: {quality_interpretation}")
    
    print()
    
    # 5. RESUMO EXECUTIVO
    print("🏆 RESUMO EXECUTIVO - ANÁLISE DE INSTRUMENTOS")
    
    overall_completion = sum([stats['completion_rate'] for stats in instrument_completeness.values()]) / len(instrument_completeness)
    overall_data_quality = sum([stats['data_quality'] for stats in validation_results.values()]) / len(validation_results)
    
    print(f"\n   📊 Métricas Gerais:")
    print(f"      • Total de instrumentos: {len(unique_instruments)}")
    print(f"      • Taxa média de completude: {overall_completion:.1f}%")
    print(f"      • Qualidade média dos dados: {overall_data_quality:.1f}%")
    print(f"      • Participantes com completude alta (≥80%): {(distribution['all_completed'] + distribution['mostly_completed'])/total_participants*100:.1f}%")
    
    print(f"\n   🎯 Interpretação para leigos:")
    if overall_completion >= 80 and overall_data_quality >= 80:
        print("      ✅ EXCELENTE! O projeto tem dados de alta qualidade e boa participação.")
    elif overall_completion >= 70 and overall_data_quality >= 70:
        print("      ✅ MUITO BOM! O projeto tem dados sólidos para análises científicas.")
    elif overall_completion >= 60 and overall_data_quality >= 60:
        print("      ⚠️ BOM! O projeto tem dados utilizáveis mas pode melhorar.")
    else:
        print("      ⚠️ PRECISA MELHORAR! Os dados têm qualidade insuficiente para algumas análises.")
    
    print(f"\n   📋 Instrumentos com melhor performance:")
    # Top 3 instrumentos por taxa de completude
    sorted_instruments = sorted(instrument_completeness.items(), key=lambda x: x[1]['completion_rate'], reverse=True)
    for i, (field, stats) in enumerate(sorted_instruments[:3], 1):
        print(f"      {i}. {instrument_names[field]}: {stats['completion_rate']:.1f}%")
    
    print(f"\n   ⚠️ Instrumentos que precisam atenção:")
    # Bottom 3 instrumentos por taxa de completude
    for i, (field, stats) in enumerate(sorted_instruments[-3:], 1):
        print(f"      {i}. {instrument_names[field]}: {stats['completion_rate']:.1f}%")
    
    # Recomendações específicas
    print(f"\n   💡 RECOMENDAÇÕES PARA MELHORAR:")
    low_completion = [field for field, stats in instrument_completeness.items() if stats['completion_rate'] < 70]
    if low_completion:
        print("      • Focar esforços nos instrumentos com baixa completude")
        print("      • Simplificar questionários muito longos")
        print("      • Melhorar instruções para participantes")
    
    if overall_data_quality < 80:
        print("      • Implementar validação em tempo real")
        print("      • Treinar equipa para melhor qualidade de dados")
        print("      • Adicionar campos obrigatórios nos instrumentos críticos")

if __name__ == "__main__":
    validate_instruments_analysis()