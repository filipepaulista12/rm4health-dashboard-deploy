#!/usr/bin/env python3
"""Script para validar métricas EFMI25 com explicações para leigos"""

from local_redcap_client import LocalREDCapClient

def validate_efmi25_metrics():
    print("=== VALIDAÇÃO MÉTRICAS EFMI25 CONFERENCE ===")
    print("Calculando indicadores específicos para apresentação científica na Europa\n")
    
    # Carregar dados
    client = LocalREDCapClient()
    data = client.get_records(raw_or_label='raw')
    
    if not data:
        print("❌ Dados não disponíveis")
        return
    
    total_records = len(data)
    print(f"📊 Analisando {total_records} registos de dados...\n")
    
    # 1. RESEARCH READINESS SCORE
    print("🎓 1. RESEARCH READINESS SCORE")
    print("   O que é: Mede se o projeto está pronto para publicação científica")
    
    complete_records = len([r for r in data if len([k for k in r.keys() if r[k] is not None and r[k] != '']) > len(r.keys()) * 0.8])
    research_readiness = (complete_records / total_records * 100) if total_records > 0 else 0
    
    print(f"   Como calcular:")
    print(f"   • Total de registos: {total_records}")
    print(f"   • Registos com >80% campos preenchidos: {complete_records}")
    print(f"   • Cálculo: {complete_records}/{total_records} × 100 = {research_readiness:.1f}%")
    print(f"   📈 Resultado: {research_readiness:.1f}% - {'Excelente!' if research_readiness >= 80 else 'Muito bom!' if research_readiness >= 70 else 'Bom!' if research_readiness >= 60 else 'Precisa melhorar'}")
    print()
    
    # 2. PUBLICATION IMPACT POTENTIAL
    print("⭐ 2. PUBLICATION IMPACT POTENTIAL")
    print("   O que é: Estima quantas 'estrelas' o projeto merece para publicação")
    
    unique_participants = len(set([r.get('participant_code', r.get('record_id', idx)) for idx, r in enumerate(data)]))
    unique_instruments = len(set([k.split('_')[0] for r in data for k in r.keys() if '_complete' in k]))
    field_coverage = len(set([k for r in data for k in r.keys()])) / 100
    
    sample_score = min(5, unique_participants / 5)
    instrument_score = min(5, unique_instruments / 2)
    quality_score = min(5, field_coverage)
    publication_impact = round((sample_score + instrument_score + quality_score) / 3, 1)
    
    print(f"   Como calcular:")
    print(f"   • Score da amostra: {unique_participants} participantes ÷ 5 = {sample_score:.1f} estrelas")
    print(f"   • Score dos instrumentos: {unique_instruments} instrumentos ÷ 2 = {instrument_score:.1f} estrelas")
    print(f"   • Score de qualidade: {len(set([k for r in data for k in r.keys()]))} campos ÷ 100 = {quality_score:.1f} estrelas")
    print(f"   • Média: ({sample_score:.1f} + {instrument_score:.1f} + {quality_score:.1f}) ÷ 3")
    print(f"   ⭐ Resultado: {publication_impact}/5 estrelas - {'Impacto muito alto!' if publication_impact >= 4 else 'Impacto alto!' if publication_impact >= 3 else 'Impacto moderado!' if publication_impact >= 2 else 'Impacto baixo'}")
    print()
    
    # 3. FHIR COMPLIANCE
    print("🌐 3. FHIR COMPLIANCE LEVEL")
    print("   O que é: Compatibilidade com padrões internacionais de saúde digital")
    
    fhir_patient_mappings = len([r for r in data if any(field in r for field in ['participant_code', 'record_id'])])
    fhir_observation_mappings = len([k for r in data for k in r.keys() if any(obs in k.lower() for obs in ['score', 'value', 'measure'])])
    fhir_condition_mappings = len([k for r in data for k in r.keys() if any(cond in k.lower() for cond in ['diagnosis', 'condition', 'disease'])])
    
    total_fhir_score = (fhir_patient_mappings + fhir_observation_mappings + fhir_condition_mappings) / (total_records * 3) * 100
    
    if total_fhir_score >= 70:
        fhir_level = "Advanced"
        fhir_explanation = "Sistema muito bem preparado para integrar com outros sistemas europeus"
    elif total_fhir_score >= 40:
        fhir_level = "Intermediate"
        fhir_explanation = "Sistema razoavelmente preparado, mas precisa alguns ajustes"
    else:
        fhir_level = "Basic"
        fhir_explanation = "Sistema básico, precisa melhorias para integração internacional"
    
    print(f"   Como calcular:")
    print(f"   • Mapeamento de pacientes: {fhir_patient_mappings}")
    print(f"   • Observações clínicas: {fhir_observation_mappings}")
    print(f"   • Condições de saúde: {fhir_condition_mappings}")
    print(f"   • Total FHIR: ({fhir_patient_mappings} + {fhir_observation_mappings} + {fhir_condition_mappings}) ÷ ({total_records} × 3) × 100")
    print(f"   🌐 Resultado: {fhir_level} ({total_fhir_score:.1f}%) - {fhir_explanation}")
    print()
    
    # 4. INNOVATION INDEX
    print("💡 4. INNOVATION INDEX")
    print("   O que é: Quantas tecnologias inovadoras o projeto usa")
    
    has_mobile_data = any('mobile' in str(r.keys()).lower() or 'app' in str(r.keys()).lower() for r in data)
    has_iot_data = any('sensor' in str(r.keys()).lower() or 'device' in str(r.keys()).lower() for r in data)
    has_ai_features = any('prediction' in str(r.keys()).lower() or 'ml' in str(r.keys()).lower() for r in data)
    has_realtime_monitoring = any('real' in str(r.keys()).lower() or 'continuous' in str(r.keys()).lower() for r in data)
    
    innovation_features = [has_mobile_data, has_iot_data, has_ai_features, has_realtime_monitoring]
    innovation_index = sum(innovation_features) / len(innovation_features) * 100
    
    print(f"   Como calcular:")
    print(f"   • Mobile Health: {'✓ Sim' if has_mobile_data else '✗ Não'}")
    print(f"   • IoT Sensors: {'✓ Sim' if has_iot_data else '✗ Não'}")
    print(f"   • AI/Machine Learning: {'✓ Sim' if has_ai_features else '✗ Não'}")
    print(f"   • Monitorização em tempo real: {'✓ Sim' if has_realtime_monitoring else '✗ Não'}")
    print(f"   • Cálculo: {sum(innovation_features)} funcionalidades ÷ 4 × 100")
    print(f"   💡 Resultado: {innovation_index:.1f}% - {'Muito inovador!' if innovation_index >= 75 else 'Inovador!' if innovation_index >= 50 else 'Moderadamente inovador!' if innovation_index >= 25 else 'Tecnologia básica'}")
    print()
    
    # 5. ELDERLY-CARE FOCUS
    print("👴 5. ELDERLY-CARE FOCUS SCORE")
    print("   O que é: Quão bem o sistema está adaptado para cuidar de idosos")
    
    elderly_instruments = ['barthel', 'iadl', 'eq5d', 'mini_mental', 'gds']
    elderly_coverage = sum([1 for inst in elderly_instruments if any(inst in str(r.keys()).lower() for r in data)]) / len(elderly_instruments) * 100
    functional_assessments = len([k for r in data for k in r.keys() if any(func in k.lower() for func in ['functional', 'mobility', 'independence', 'adl'])])
    elderly_focus_score = (elderly_coverage + min(100, functional_assessments / total_records * 50)) / 2
    
    print(f"   Como calcular:")
    print(f"   • Instrumentos específicos para idosos encontrados:")
    for inst in elderly_instruments:
        found = any(inst in str(r.keys()).lower() for r in data)
        print(f"     - {inst.upper()}: {'✓ Sim' if found else '✗ Não'}")
    print(f"   • Cobertura de instrumentos: {sum([1 for inst in elderly_instruments if any(inst in str(r.keys()).lower() for r in data)])}/5 × 100 = {elderly_coverage:.1f}%")
    print(f"   • Avaliações funcionais encontradas: {functional_assessments}")
    print(f"   👴 Resultado: {elderly_focus_score:.1f}% - {'Muito bem focado em idosos!' if elderly_focus_score >= 80 else 'Bem focado!' if elderly_focus_score >= 60 else 'Moderadamente focado!' if elderly_focus_score >= 40 else 'Precisa mais foco em idosos'}")
    print()
    
    # 6. DATA QUALITY METRICS
    print("📊 6. DATA QUALITY SCORE")
    print("   O que é: Qualidade geral dos dados coletados")
    
    missing_data_rate = sum([len([k for k in r.keys() if r[k] is None or r[k] == '']) for r in data]) / (total_records * len(data[0].keys()) if data else 1) * 100
    data_consistency_score = 100 - (len(set([len(r.keys()) for r in data])) / total_records * 100)
    temporal_consistency = len([r for r in data if any('date' in k.lower() for k in r.keys())]) / total_records * 100
    overall_data_quality = (100 - missing_data_rate + data_consistency_score + temporal_consistency) / 3
    
    print(f"   Como calcular:")
    print(f"   • Taxa de dados em falta: {missing_data_rate:.1f}%")
    print(f"   • Consistência dos campos: {data_consistency_score:.1f}%")
    print(f"   • Consistência temporal: {temporal_consistency:.1f}%")
    print(f"   • Média: (100 - {missing_data_rate:.1f} + {data_consistency_score:.1f} + {temporal_consistency:.1f}) ÷ 3")
    print(f"   📊 Resultado: {overall_data_quality:.1f}% - {'Qualidade excelente!' if overall_data_quality >= 90 else 'Qualidade muito boa!' if overall_data_quality >= 80 else 'Qualidade boa!' if overall_data_quality >= 70 else 'Qualidade razoável!'}")
    print()
    
    # 7. CONFERENCE READINESS
    print("🎯 7. CONFERENCE READINESS")
    print("   O que é: Se o projeto está pronto para apresentar numa conferência científica")
    
    has_baseline_data = len(data) >= 20
    has_longitudinal_data = len([r for r in data if any('repeat' in k.lower() for k in r.keys())]) > 0
    has_outcome_measures = len([k for r in data for k in r.keys() if any(outcome in k.lower() for outcome in ['score', 'total', 'result'])]) > 0
    has_demographic_data = any(demo in str(data[0].keys()).lower() for demo in ['age', 'sex', 'birth'])
    
    readiness_criteria = [has_baseline_data, has_longitudinal_data, has_outcome_measures, has_demographic_data]
    conference_readiness = sum(readiness_criteria) / len(readiness_criteria) * 100
    
    print(f"   Critérios de prontidão:")
    print(f"   • Amostra mínima (≥20): {'✓ Sim' if has_baseline_data else '✗ Não'} ({len(data)} registos)")
    print(f"   • Dados longitudinais: {'✓ Sim' if has_longitudinal_data else '✗ Não'}")
    print(f"   • Medidas de resultado: {'✓ Sim' if has_outcome_measures else '✗ Não'}")
    print(f"   • Demografia completa: {'✓ Sim' if has_demographic_data else '✗ Não'}")
    print(f"   • Cálculo: {sum(readiness_criteria)} critérios ÷ 4 × 100")
    print(f"   🎯 Resultado: {conference_readiness:.1f}% - {'Totalmente pronto!' if conference_readiness >= 80 else 'Bem preparado!' if conference_readiness >= 60 else 'Parcialmente pronto!' if conference_readiness >= 40 else 'Precisa mais preparação'}")
    print()
    
    # RESUMO FINAL
    print("🏆 RESUMO EXECUTIVO PARA EFMI25:")
    print(f"   📈 Research Readiness: {research_readiness:.1f}%")
    print(f"   ⭐ Publication Impact: {publication_impact}/5 estrelas")
    print(f"   🌐 FHIR Compliance: {fhir_level} ({total_fhir_score:.1f}%)")
    print(f"   💡 Innovation Index: {innovation_index:.1f}%")
    print(f"   👴 Elderly Focus: {elderly_focus_score:.1f}%")
    print(f"   📊 Data Quality: {overall_data_quality:.1f}%")
    print(f"   🎯 Conference Readiness: {conference_readiness:.1f}%")
    
    overall_score = (research_readiness + publication_impact*20 + total_fhir_score + innovation_index + elderly_focus_score + overall_data_quality + conference_readiness) / 7
    print(f"\n🎖️ SCORE GERAL EFMI25: {overall_score:.1f}/100")
    
    if overall_score >= 80:
        recommendation = "RECOMENDAÇÃO: Submeter para apresentação oral principal!"
    elif overall_score >= 70:
        recommendation = "RECOMENDAÇÃO: Submeter para apresentação oral ou poster!"
    elif overall_score >= 60:
        recommendation = "RECOMENDAÇÃO: Submeter para poster com melhorias!"
    else:
        recommendation = "RECOMENDAÇÃO: Melhorar projeto antes de submeter!"
    
    print(f"✅ {recommendation}")

if __name__ == "__main__":
    validate_efmi25_metrics()