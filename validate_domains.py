#!/usr/bin/env python3
"""Script para validar os 4 domínios de qualidade"""

from local_redcap_client import LocalREDCapClient

def validate_domains_assessment():
    print("=== VALIDAÇÃO DOS 4 DOMÍNIOS DE QUALIDADE ===")
    
    # Carregar dados
    client = LocalREDCapClient()
    data = client.get_records(raw_or_label='raw')
    
    print(f"📊 Analisando {len(data)} registros para os 4 domínios...")
    
    if not data:
        print("❌ Dados não disponíveis")
        return
    
    # 1. DOMÍNIO TÉCNICO
    print(f"\n🔧 DOMÍNIO TÉCNICO:")
    data_completeness = len([r for r in data if len(r.keys()) > 5]) / len(data) * 100
    field_consistency = len(set([len(r.keys()) for r in data])) / len(data) * 100
    technical_score = (data_completeness + field_consistency) / 2
    
    print(f"  Completude dos dados: {data_completeness:.1f}%")
    print(f"  Consistência de campos: {field_consistency:.1f}%")
    print(f"  📈 Score Técnico: {technical_score:.1f}")
    
    # FHIR compliance
    fhir_patient_count = len([r for r in data if 'record_id' in r])
    fhir_observation_count = len([k for r in data for k in r.keys() if any(obs in k.lower() for obs in ['score', 'value', 'measure', 'assessment'])])
    fhir_medication_count = len([k for r in data for k in r.keys() if any(med in k.lower() for med in ['med', 'drug', 'pill', 'medication'])])
    fhir_condition_count = len([k for r in data for k in r.keys() if any(cond in k.lower() for cond in ['condition', 'diagnosis', 'disease', 'health'])])
    
    total_fhir_mappings = fhir_patient_count + fhir_observation_count + fhir_medication_count + fhir_condition_count
    fhir_compliance_score = min(90, (total_fhir_mappings / len(data)) * 10) if data else 0
    
    print(f"  FHIR Patient: {fhir_patient_count} | Observation: {fhir_observation_count}")
    print(f"  FHIR Medication: {fhir_medication_count} | Condition: {fhir_condition_count}")
    print(f"  🌐 FHIR Compliance: {fhir_compliance_score:.1f}")
    
    # 2. DOMÍNIO ÉTICO
    print(f"\n⚖️ DOMÍNIO ÉTICO:")
    has_consent_fields = any('consent' in str(r.keys()).lower() for r in data)
    has_privacy_fields = any('privacy' in str(r.keys()).lower() or 'confidential' in str(r.keys()).lower() for r in data)
    data_anonymization = len([r for r in data if 'record_id' in r and not any(field.lower() in ['name', 'email', 'phone'] for field in r.keys())]) / len(data) * 100
    ethical_score = (data_anonymization + (50 if has_consent_fields else 0) + (30 if has_privacy_fields else 0)) / 1.8
    
    print(f"  Campos de consentimento: {'✓' if has_consent_fields else '✗'}")
    print(f"  Campos de privacidade: {'✓' if has_privacy_fields else '✗'}")
    print(f"  Anonimização de dados: {data_anonymization:.1f}%")
    print(f"  📈 Score Ético: {ethical_score:.1f}")
    
    # 3. DOMÍNIO ORGANIZACIONAL
    print(f"\n🏢 DOMÍNIO ORGANIZACIONAL:")
    consistent_collection = len(set([len([k for k in r.keys() if r[k] is not None and r[k] != '']) for r in data])) / len(data) * 100
    standardized_fields = len(set([tuple(sorted(r.keys())) for r in data])) / len(data) * 100  
    organizational_score = (consistent_collection + (100 - standardized_fields)) / 2
    
    print(f"  Coleta consistente: {consistent_collection:.1f}%")
    print(f"  Campos padronizados: {standardized_fields:.1f}%")
    print(f"  📈 Score Organizacional: {organizational_score:.1f}")
    
    # 4. DOMÍNIO CLÍNICO
    print(f"\n🏥 DOMÍNIO CLÍNICO:")
    clinical_instruments = ['eq5d', 'psqi', 'barthel', 'moca', 'gds', 'iadl']
    instrument_coverage = sum([1 for inst in clinical_instruments if any(inst in str(r.keys()).lower() for r in data)]) / len(clinical_instruments) * 100
    clinical_data_completeness = len([r for r in data if any(inst in str(r.keys()).lower() for inst in clinical_instruments)]) / len(data) * 100
    clinical_score = (instrument_coverage + clinical_data_completeness) / 2
    
    print(f"  Cobertura de instrumentos: {instrument_coverage:.1f}%")
    print(f"  Completude clínica: {clinical_data_completeness:.1f}%")
    print(f"  📈 Score Clínico: {clinical_score:.1f}")
    
    # RESUMO FINAL
    print(f"\n📊 RESUMO DOS 4 DOMÍNIOS:")
    print(f"  🔧 Técnico: {technical_score:.1f}")
    print(f"  ⚖️ Ético: {ethical_score:.1f}")
    print(f"  🏢 Organizacional: {organizational_score:.1f}")
    print(f"  🏥 Clínico: {clinical_score:.1f}")
    
    overall_score = (technical_score + ethical_score + organizational_score + clinical_score) / 4
    print(f"\n🎯 SCORE GERAL: {overall_score:.1f}/100")
    
    # Contadores adicionais
    total_participants = len(set([r.get('record_id', r.get('participant_id', idx)) for idx, r in enumerate(data)]))
    total_instruments = len(set([k.split('_')[0] for r in data for k in r.keys() if '_' in k]))
    total_assessments = len([k for r in data for k in r.keys() if any(assess in k.lower() for assess in ['score', 'total', 'assessment', 'questionnaire'])])
    
    print(f"\n📋 DADOS ADICIONAIS:")
    print(f"  Participantes únicos: {total_participants}")
    print(f"  Total de instrumentos: {total_instruments}")
    print(f"  Avaliações disponíveis: {total_assessments}")

if __name__ == "__main__":
    validate_domains_assessment()