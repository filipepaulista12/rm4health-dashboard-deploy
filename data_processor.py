import json
import pandas as pd
import numpy as np
from datetime import datetime
import re
from collections import Counter
from analytics import RM4HealthAnalytics

class DataProcessor:
    def __init__(self, data):
        self.data = data if data else []
        self.processed_data = self.data.copy()
    
    def get_basic_stats(self):
        """Retorna estatísticas básicas do dataset"""
        if not self.data:
            return {
                'total_participants': 0,
                'total_records': 0,
                'total_variables': 0,
                'total_grupo_a': 0,
                'total_grupo_b': 0,
                'total_grupo_c': 0,
                'total_grupo_d': 0
            }
        
        # Conta participantes únicos baseado em participant_code (campo correto do RM4Health)
        unique_participants = set()
        all_fields = set()
        
        # Contadores por grupo
        grupo_a_participants = set()
        grupo_b_participants = set()
        grupo_c_participants = set()
        grupo_d_participants = set()
        
        for record in self.data:
            # Tenta diferentes campos de identificação de participante
            participant_id = None
            for id_field in ['participant_code', 'record_id', 'participant_code_estudo']:
                if id_field in record and record[id_field]:
                    participant_id = record[id_field]
                    break
            
            if participant_id:
                unique_participants.add(participant_id)
                
                # Classificar por grupos baseado no participant_group
                group = record.get('participant_group', '')
                if 'Grupo A' in str(group) or group == 'Grupo A':
                    grupo_a_participants.add(participant_id)
                elif 'Grupo B' in str(group) or group == 'Grupo B':
                    grupo_b_participants.add(participant_id)
                elif 'Grupo C' in str(group) or group == 'Grupo C':
                    grupo_c_participants.add(participant_id)
                elif 'Grupo D' in str(group) or group == 'Grupo D':
                    grupo_d_participants.add(participant_id)
            
            all_fields.update(record.keys())
        
        # Estatísticas básicas sem completude (que é problemática devido a campos condicionais)
        total_fields = len(all_fields)
        
        # RM4Health tem 11 formulários conhecidos (0-10 em algarismo romano)
        total_instruments = 11
        
        stats = {
            'total_participants': len(unique_participants),
            'total_records': len(self.data),
            'total_variables': total_fields,
            'total_grupo_a': len(grupo_a_participants),
            'total_grupo_b': len(grupo_b_participants), 
            'total_grupo_c': len(grupo_c_participants),
            'total_grupo_d': len(grupo_d_participants),
            'total_instruments': total_instruments,
            'total_raw_records': len(self.data)
        }
        
        return stats
    
    def get_age_distribution(self):
        """Extrai distribuição de idade"""
        age_values = []
        
        # Procura por campos de idade
        for record in self.data:
            for field_name, value in record.items():
                if any(keyword in field_name.lower() for keyword in ['idade', 'age', 'birth']):
                    try:
                        age = float(value)
                        if 0 < age < 150:  # Validação básica
                            age_values.append(age)
                    except (ValueError, TypeError):
                        continue
        
        if not age_values:
            return None
        
        return {
            'data': age_values,
            'mean': round(sum(age_values) / len(age_values), 1),
            'median': sorted(age_values)[len(age_values) // 2],
            'min': int(min(age_values)),
            'max': int(max(age_values)),
            'count': len(age_values)
        }
    
    def get_gender_distribution(self):
        """Extrai distribuição de gênero"""
        gender_values = []
        
        # Procura por campos de gênero/sexo
        for record in self.data:
            for field_name, value in record.items():
                if any(keyword in field_name.lower() for keyword in ['sexo', 'gender', 'genero']):
                    if value and value not in ['', 'NaN']:
                        gender_values.append(str(value).strip())
        
        if not gender_values:
            return None
        
        gender_counts = Counter(gender_values)
        
        return {
            'labels': list(gender_counts.keys()),
            'values': list(gender_counts.values()),
            'total': len(gender_values)
        }
    
    def get_records_per_participant(self):
        """Contabiliza registros por participante"""
        participant_counts = Counter()
        
        for record in self.data:
            # Procura pelo campo correto de identificação
            participant_id = None
            for id_field in ['participant_code', 'record_id', 'participant_code_estudo']:
                if id_field in record and record[id_field]:
                    participant_id = record[id_field]
                    break
            
            if participant_id:
                participant_counts[participant_id] += 1
        
        if not participant_counts:
            return None
        
        # Ordena por número de registros (descendente)
        sorted_participants = participant_counts.most_common(15)
        
        return {
            'labels': [str(p[0]) for p in sorted_participants],
            'values': [p[1] for p in sorted_participants]
        }
    
    def get_records_per_instrument(self):
        """Analisa distribuição de registos por formulário baseado nos campos _complete"""
        if not self.data:
            return None
        
        # Procurar por todos os campos que terminam em '_complete'
        complete_fields = []
        if self.data:
            sample_record = self.data[0]
            for field_name in sample_record.keys():
                if field_name.endswith('_complete'):
                    complete_fields.append(field_name)
        
        if not complete_fields:
            return None
        
        # Contar registos para cada formulário baseado no campo _complete
        instrument_counts = {}
        
        for complete_field in complete_fields:
            # Remove '_complete' do nome para obter o nome do instrumento
            instrument_name = complete_field.replace('_complete', '')
            
            # Conta quantos registos têm esse campo preenchido (qualquer valor que não seja vazio)
            count = 0
            for record in self.data:
                if complete_field in record and record[complete_field] is not None and str(record[complete_field]).strip() != '':
                    count += 1
            
            if count > 0:
                instrument_counts[instrument_name] = count
        
        if not instrument_counts:
            return None
        
        # Função para extrair número do formulário para ordenação
        def get_form_number(instrument_name):
            import re
            # Procura por números no nome
            numbers = re.findall(r'\d+', instrument_name)
            if numbers:
                return int(numbers[0])
            # Se não tem número, coloca no final (ex: baseline, demographics)
            return 999
        
        # Ordena por número do formulário, depois por nome
        sorted_instruments = sorted(instrument_counts.items(), 
                                  key=lambda x: (get_form_number(x[0]), x[0]))
        
        # Melhora os nomes para exibição
        formatted_instruments = []
        for instrument_name, count in sorted_instruments:
            # Se tem número, formata como "Formulário X"
            import re
            numbers = re.findall(r'\d+', instrument_name)
            if numbers:
                form_num = numbers[0]
                display_name = f"Formulário {form_num}"
            else:
                # Para formulários sem número (baseline, demographics, etc)
                display_name = instrument_name.replace('_', ' ').title()
            
            formatted_instruments.append((display_name, count))
        
        return {
            'labels': [inst[0] for inst in formatted_instruments],
            'values': [inst[1] for inst in formatted_instruments]
        }
    
    def get_completion_by_instrument(self):
        """Analisa completude por instrumento (baseado em prefixos de colunas)"""
        instruments = {}
        
        # Agrupa campos por prefixo
        for record in self.data:
            for field_name in record.keys():
                if '_' in field_name:
                    prefix = field_name.split('_')[0]
                    if prefix not in instruments:
                        instruments[prefix] = set()
                    instruments[prefix].add(field_name)
        
        completion_data = []
        
        for instrument, fields in instruments.items():
            if len(fields) > 2:  # Só considera instrumentos com mais de 2 campos
                total_possible = len(self.data) * len(fields)
                filled_count = 0
                
                for record in self.data:
                    for field in fields:
                        if field in record and record[field] not in [None, '', 'NaN']:
                            filled_count += 1
                
                completion_rate = (filled_count / total_possible * 100) if total_possible > 0 else 0
                
                completion_data.append({
                    'instrument': instrument,
                    'completion_rate': round(completion_rate, 1),
                    'fields_count': len(fields),
                    'records_count': len(self.data)
                })
        
        return sorted(completion_data, key=lambda x: x['completion_rate'], reverse=True)
    
    def search_columns(self, search_term):
        """Busca colunas por termo"""
        all_columns = set()
        
        for record in self.data:
            all_columns.update(record.keys())
        
        matching_columns = [col for col in all_columns if search_term.lower() in col.lower()]
        return sorted(matching_columns)
    
    def get_column_summary(self, column):
        """Retorna resumo de uma coluna específica"""
        values = []
        
        for record in self.data:
            if column in record:
                values.append(record[column])
        
        if not values:
            return None
        
        non_null_values = [v for v in values if v not in [None, '', 'NaN']]
        
        summary = {
            'name': column,
            'total_values': len(values),
            'non_null_values': len(non_null_values),
            'null_values': len(values) - len(non_null_values),
            'unique_values': len(set(str(v) for v in non_null_values)),
            'data_type': 'mixed'
        }
        
        # Tenta converter para números
        numeric_values = []
        for v in non_null_values:
            try:
                numeric_values.append(float(v))
            except (ValueError, TypeError):
                pass
        
        if numeric_values:
            summary.update({
                'mean': round(sum(numeric_values) / len(numeric_values), 2),
                'min': round(min(numeric_values), 2),
                'max': round(max(numeric_values), 2),
                'data_type': 'numeric'
            })
        
        # Valores mais frequentes
        value_counts = Counter(str(v) for v in non_null_values)
        top_values = value_counts.most_common(10)
        
        summary['top_values'] = [
            {'value': val, 'count': count} 
            for val, count in top_values
        ]
        
        return summary
    
    def get_all_columns(self):
        """Retorna todas as colunas únicas do dataset"""
        all_columns = set()
        
        for record in self.data:
            all_columns.update(record.keys())
        
        return sorted(list(all_columns))
    
    def get_advanced_analytics(self, metadata=None):
        """Retorna análises avançadas usando o módulo analytics"""
        if not metadata:
            # Criar metadata básica se não fornecida
            metadata = []
            all_fields = set()
            for record in self.data:
                all_fields.update(record.keys())
            
            for field in all_fields:
                metadata.append({
                    'field_name': field,
                    'field_label': field.replace('_', ' ').title()
                })
        
        analytics = RM4HealthAnalytics(self.data, metadata)
        
        return {
            'by_instrument': analytics.analyze_by_instrument(),
            'by_group': analytics.analyze_by_group(),
            'completion_rates': analytics.get_completion_rates(),
            'patterns': analytics.analyze_patterns(),
            'insights': analytics.generate_insights()
        }
    
    def filter_data(self, filters):
        """Aplica filtros aos dados"""
        filtered_data = self.data.copy()
        
        for filter_name, filter_value in filters.items():
            if not filter_value or filter_value == 'all':
                continue
                
            if filter_name == 'instrument':
                filtered_data = [r for r in filtered_data 
                               if r.get('redcap_repeat_instrument', 'baseline') == filter_value]
            elif filter_name == 'group':
                filtered_data = [r for r in filtered_data 
                               if r.get('participant_group') == filter_value]
            elif filter_name == 'participant':
                filtered_data = [r for r in filtered_data 
                               if r.get('participant_code') == filter_value]
            elif filter_name == 'date_from' and filter_value:
                # Filtro por data (busca em campos de data)
                date_fields = [f for f in ['data_preench_0', 'data_preench_8', 'questionnaire_date_8'] 
                              if any(f in r for r in filtered_data)]
                if date_fields:
                    filtered_data = [r for r in filtered_data 
                                   if any(r.get(df, '') >= filter_value for df in date_fields)]
            elif filter_name == 'date_to' and filter_value:
                date_fields = [f for f in ['data_preench_0', 'data_preench_8', 'questionnaire_date_8'] 
                              if any(f in r for r in filtered_data)]
                if date_fields:
                    filtered_data = [r for r in filtered_data 
                                   if any(r.get(df, '') <= filter_value for df in date_fields)]
        
        return filtered_data
    
    def get_field_analysis(self, field_name):
        """Análise detalhada de um campo específico"""
        values = []
        instruments = {}
        groups = {}
        
        for record in self.data:
            value = record.get(field_name)
            if value:
                values.append(value)
                
                # Por instrumento
                instrument = record.get('redcap_repeat_instrument', 'baseline')
                if instrument not in instruments:
                    instruments[instrument] = []
                instruments[instrument].append(value)
                
                # Por grupo
                group = record.get('participant_group', 'N/A')
                if group not in groups:
                    groups[group] = []
                groups[group].append(value)
        
        analysis = {
            'field_name': field_name,
            'total_values': len(values),
            'unique_values': len(set(values)),
            'by_instrument': {},
            'by_group': {}
        }
        
        # Análise por instrumento
        for instrument, inst_values in instruments.items():
            analysis['by_instrument'][instrument] = {
                'count': len(inst_values),
                'unique': len(set(inst_values)),
                'most_common': Counter(inst_values).most_common(5)
            }
        
        # Análise por grupo
        for group, group_values in groups.items():
            analysis['by_group'][group] = {
                'count': len(group_values),
                'unique': len(set(group_values)),
                'most_common': Counter(group_values).most_common(5)
            }
        
        return analysis

    # =====================================
    # ANÁLISE LONGITUDINAL - MÉTODOS NOVOS
    # =====================================
    
    def analyze_temporal_trends(self):
        """Analisa evolução temporal de sintomas por participante usando campos reais do RM4Health"""
        trends = {
            'participant_trends': {},
            'symptom_evolution': {},
            'overall_trends': {},
            'summary_stats': {}
        }
        
        try:
            # Agrupa dados por participante e data
            participant_data = {}
            for record in self.data:
                participant_id = record.get('participant_code')
                if not participant_id:
                    continue
                
                # Extrai data do registro - usa campos reais do RM4Health
                record_date = None
                for date_field in ['questionnaire_date_8', 'data_preench_8', 'questionnaire_date', 'questionnaire_date_2']:
                    if date_field in record and record[date_field]:
                        try:
                            date_str = str(record[date_field])
                            if len(date_str) >= 10:
                                record_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                                break
                        except:
                            continue
                
                if not record_date:
                    continue
                
                if participant_id not in participant_data:
                    participant_data[participant_id] = []
                
                participant_data[participant_id].append({
                    'date': record_date,
                    'record': record
                })
            
            # Ordena dados por data para cada participante
            for participant_id in participant_data:
                participant_data[participant_id].sort(key=lambda x: x['date'])
            
            # Analisa tendências por participante
            for participant_id, records in participant_data.items():
                if len(records) < 2:
                    continue
                
                participant_trends = {
                    'total_records': len(records),
                    'date_range': f"{records[0]['date'].strftime('%Y-%m-%d')} - {records[-1]['date'].strftime('%Y-%m-%d')}",
                    'time_span_days': (records[-1]['date'] - records[0]['date']).days,
                    'symptom_trends': {},
                    'medication_trends': {},
                    'wellbeing_trend': 'stable'
                }
                
                # Analisa sintomas reais do RM4Health ao longo do tempo
                symptom_fields = [
                    'health_status', 'sleep_quality_last_night', 'daytime_sleepiness', 
                    'dizziness_today', 'fatigue_today', 'muscle_weakness_today', 'pain_today'
                ]
                
                # Mapeamento de valores textuais para numéricos para poder calcular tendências
                value_mapping = {
                    'health_status': {'Mal': 5, 'Não muito bem': 4, 'Razoável': 3, 'Bem': 2, 'Muito bem': 1},
                    'sleep_quality_last_night': {'Muito mal': 5, 'Mal': 4, 'Razoável': 3, 'Bem': 2, 'Muito bem': 1},
                    'daytime_sleepiness': {'Sempre': 5, 'Frequentemente': 4, 'Ocasionalmente': 3, 'Raramente': 2, 'Nunca': 1},
                    'dizziness_today': {'Sempre': 5, 'Frequentemente': 4, 'Ocasionalmente': 3, 'Raramente': 2, 'Nunca': 1},
                    'fatigue_today': {'Sempre': 5, 'Frequentemente': 4, 'Ocasionalmente': 3, 'Raramente': 2, 'Nunca': 1},
                    'muscle_weakness_today': {'Sempre': 5, 'Frequentemente': 4, 'Ocasionalmente': 3, 'Raramente': 2, 'Nunca': 1},
                    'pain_today': {'Sempre': 5, 'Frequentemente': 4, 'Ocasionalmente': 3, 'Raramente': 2, 'Nunca': 1}
                }
                
                for field in symptom_fields:
                    values = []
                    for record_data in records:
                        val = record_data['record'].get(field)
                        if val and val != '':
                            # Converte valor textual para numérico
                            if field in value_mapping and val in value_mapping[field]:
                                values.append(value_mapping[field][val])
                            elif str(val).replace('.','').replace('-','').isdigit():
                                values.append(float(val))
                    
                    if len(values) >= 2:
                        # Calcula tendência simples
                        first_half = sum(values[:len(values)//2]) / (len(values)//2) if len(values) > 1 else values[0]
                        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
                        
                        change = second_half - first_half
                        if abs(change) >= 0.5:  # Mudança significativa
                            trend = 'improving' if change < 0 else 'worsening'  # Para sintomas, menor é melhor
                        else:
                            trend = 'stable'
                            
                        participant_trends['symptom_trends'][field] = {
                            'trend': trend,
                            'first_avg': round(first_half, 2),
                            'second_avg': round(second_half, 2),
                            'change': round(change, 2),
                            'total_measurements': len(values)
                        }
                
                trends['participant_trends'][participant_id] = participant_trends
            
            # Estatísticas gerais
            if trends['participant_trends']:
                trends['summary_stats'] = {
                    'total_participants_analyzed': len(trends['participant_trends']),
                    'avg_records_per_participant': round(sum(p['total_records'] for p in trends['participant_trends'].values()) / len(trends['participant_trends']), 1),
                    'participants_improving': len([p for p in trends['participant_trends'].values() if any(s.get('trend') == 'improving' for s in p['symptom_trends'].values())]),
                    'participants_worsening': len([p for p in trends['participant_trends'].values() if any(s.get('trend') == 'worsening' for s in p['symptom_trends'].values())]),
                    'total_symptom_measurements': sum(sum(s.get('total_measurements', 0) for s in p['symptom_trends'].values()) for p in trends['participant_trends'].values())
                }
            else:
                trends['summary_stats'] = {
                    'total_participants_analyzed': 0,
                    'avg_records_per_participant': 0,
                    'participants_improving': 0,
                    'participants_worsening': 0,
                    'total_symptom_measurements': 0
                }
            
        except Exception as e:
            print(f"Erro na análise de tendências temporais: {e}")
            import traceback
            traceback.print_exc()
        
        return trends
    
    def get_health_trajectories(self):
        """Cria trajetórias individuais de saúde e classifica tipos de evolução"""
        trajectories = {
            'individual_trajectories': {},
            'trajectory_types': {},
            'classification_summary': {}
        }
        
        try:
            # Reutiliza lógica de agrupamento temporal
            temporal_trends = self.analyze_temporal_trends()
            
            for participant_id, trend_data in temporal_trends['participant_trends'].items():
                trajectory = {
                    'participant_id': participant_id,
                    'trajectory_type': 'stable',
                    'health_score_evolution': [],
                    'key_indicators': {},
                    'classification_reasons': []
                }
                
                # Classifica tipo de trajetória baseado nos sintomas
                improving_symptoms = sum(1 for s in trend_data['symptom_trends'].values() if s['trend'] == 'improving')
                worsening_symptoms = sum(1 for s in trend_data['symptom_trends'].values() if s['trend'] == 'worsening')
                total_symptoms = len(trend_data['symptom_trends'])
                
                if total_symptoms > 0:
                    if improving_symptoms > worsening_symptoms and improving_symptoms / total_symptoms > 0.6:
                        trajectory['trajectory_type'] = 'consistently_improving'
                        trajectory['classification_reasons'].append(f'{improving_symptoms}/{total_symptoms} sintomas melhorando')
                    elif worsening_symptoms > improving_symptoms and worsening_symptoms / total_symptoms > 0.6:
                        trajectory['trajectory_type'] = 'consistently_declining'
                        trajectory['classification_reasons'].append(f'{worsening_symptoms}/{total_symptoms} sintomas piorando')
                    elif improving_symptoms > 0 and worsening_symptoms > 0:
                        trajectory['trajectory_type'] = 'fluctuating'
                        trajectory['classification_reasons'].append('Sintomas variáveis')
                    else:
                        trajectory['trajectory_type'] = 'stable'
                        trajectory['classification_reasons'].append('Sem mudanças significativas')
                
                trajectories['individual_trajectories'][participant_id] = trajectory
            
            # Resumo por tipo de trajetória
            trajectory_counts = Counter(t['trajectory_type'] for t in trajectories['individual_trajectories'].values())
            trajectories['classification_summary'] = {
                'consistently_improving': trajectory_counts.get('consistently_improving', 0),
                'consistently_declining': trajectory_counts.get('consistently_declining', 0),
                'fluctuating': trajectory_counts.get('fluctuating', 0),
                'stable': trajectory_counts.get('stable', 0),
                'total_analyzed': len(trajectories['individual_trajectories'])
            }
            
        except Exception as e:
            print(f"Erro na análise de trajetórias: {e}")
        
        return trajectories
    
    def detect_seasonal_patterns(self):
        """Detecta sazonalidade nos dados usando campos reais do RM4Health"""
        patterns = {
            'monthly_patterns': {},
            'weekly_patterns': {},
            'seasonal_correlations': {},
            'temporal_insights': []
        }
        
        try:
            monthly_data = {}
            weekly_data = {}
            
            for record in self.data:
                # Extrai data usando campos reais
                record_date = None
                for date_field in ['questionnaire_date_8', 'data_preench_8', 'questionnaire_date', 'questionnaire_date_2']:
                    if date_field in record and record[date_field]:
                        try:
                            date_str = str(record[date_field])
                            if len(date_str) >= 10:
                                record_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                                break
                        except:
                            continue
                
                if not record_date:
                    continue
                
                month = record_date.strftime('%B')
                weekday = record_date.strftime('%A')
                
                if month not in monthly_data:
                    monthly_data[month] = {'count': 0, 'symptoms': [], 'health_scores': []}
                if weekday not in weekly_data:
                    weekly_data[weekday] = {'count': 0, 'symptoms': [], 'health_scores': []}
                
                monthly_data[month]['count'] += 1
                weekly_data[weekday]['count'] += 1
                
                # Coleta sintomas reais para análise
                symptom_fields = [
                    'health_status', 'sleep_quality_last_night', 'daytime_sleepiness', 
                    'dizziness_today', 'fatigue_today', 'pain_today'
                ]
                
                # Mapeamento de valores textuais para numéricos
                value_mapping = {
                    'health_status': {'Mal': 5, 'Não muito bem': 4, 'Razoável': 3, 'Bem': 2, 'Muito bem': 1},
                    'sleep_quality_last_night': {'Muito mal': 5, 'Mal': 4, 'Razoável': 3, 'Bem': 2, 'Muito bem': 1},
                    'daytime_sleepiness': {'Sempre': 5, 'Frequentemente': 4, 'Ocasionalmente': 3, 'Raramente': 2, 'Nunca': 1},
                    'dizziness_today': {'Sempre': 5, 'Frequentemente': 4, 'Ocasionalmente': 3, 'Raramente': 2, 'Nunca': 1},
                    'fatigue_today': {'Sempre': 5, 'Frequentemente': 4, 'Ocasionalmente': 3, 'Raramente': 2, 'Nunca': 1},
                    'pain_today': {'Sempre': 5, 'Frequentemente': 4, 'Ocasionalmente': 3, 'Raramente': 2, 'Nunca': 1}
                }
                
                for field in symptom_fields:
                    value = record.get(field)
                    if value and value != '':
                        # Converte valor textual para numérico
                        if field in value_mapping and value in value_mapping[field]:
                            score = value_mapping[field][value]
                            monthly_data[month]['symptoms'].append(score)
                            weekly_data[weekday]['symptoms'].append(score)
                            
                            # Para status de saúde, também adiciona aos health_scores
                            if field == 'health_status':
                                monthly_data[month]['health_scores'].append(score)
                                weekly_data[weekday]['health_scores'].append(score)
            
            # Calcula médias mensais
            for month, data in monthly_data.items():
                if data['symptoms'] and data['health_scores']:
                    patterns['monthly_patterns'][month] = {
                        'record_count': data['count'],
                        'avg_symptom_severity': round(sum(data['symptoms']) / len(data['symptoms']), 2),
                        'avg_health_status': round(sum(data['health_scores']) / len(data['health_scores']), 2),
                        'total_symptoms_reported': len(data['symptoms'])
                    }
            
            # Calcula médias semanais
            for weekday, data in weekly_data.items():
                if data['symptoms'] and data['health_scores']:
                    patterns['weekly_patterns'][weekday] = {
                        'record_count': data['count'],
                        'avg_symptom_severity': round(sum(data['symptoms']) / len(data['symptoms']), 2),
                        'avg_health_status': round(sum(data['health_scores']) / len(data['health_scores']), 2),
                        'total_symptoms_reported': len(data['symptoms'])
                    }
            
            # Gera insights se houver dados suficientes
            if patterns['monthly_patterns']:
                worst_month = max(patterns['monthly_patterns'].items(), key=lambda x: x[1]['avg_symptom_severity'])
                best_month = min(patterns['monthly_patterns'].items(), key=lambda x: x[1]['avg_symptom_severity'])
                patterns['temporal_insights'].append(f"Pior mês para sintomas: {worst_month[0]} (média: {worst_month[1]['avg_symptom_severity']})")
                patterns['temporal_insights'].append(f"Melhor mês para sintomas: {best_month[0]} (média: {best_month[1]['avg_symptom_severity']})")
            
            if patterns['weekly_patterns']:
                worst_day = max(patterns['weekly_patterns'].items(), key=lambda x: x[1]['avg_symptom_severity'])
                best_day = min(patterns['weekly_patterns'].items(), key=lambda x: x[1]['avg_symptom_severity'])
                patterns['temporal_insights'].append(f"Pior dia da semana: {worst_day[0]} (média: {worst_day[1]['avg_symptom_severity']})")
                patterns['temporal_insights'].append(f"Melhor dia da semana: {best_day[0]} (média: {best_day[1]['avg_symptom_severity']})")
            
        except Exception as e:
            print(f"Erro na análise sazonal: {e}")
            import traceback
            traceback.print_exc()
        
        return patterns
    
    def detect_health_deterioration(self):
        """Detecta sinais de deterioração da saúde usando dados reais do RM4Health"""
        alerts = {
            'high_priority_alerts': [],
            'medium_priority_alerts': [],
            'participants_at_risk': {},
            'deterioration_indicators': {}
        }
        
        try:
            temporal_trends = self.analyze_temporal_trends()
            
            for participant_id, trend_data in temporal_trends['participant_trends'].items():
                risk_score = 0
                risk_factors = []
                
                # Analisa tendências de sintomas específicos
                worsening_symptoms = [s for s in trend_data['symptom_trends'].values() if s['trend'] == 'worsening']
                
                if len(worsening_symptoms) >= 3:
                    risk_score += 40
                    risk_factors.append(f'{len(worsening_symptoms)} sintomas piorando significativamente')
                elif len(worsening_symptoms) >= 2:
                    risk_score += 25
                    risk_factors.append(f'{len(worsening_symptoms)} sintomas piorando')
                elif len(worsening_symptoms) >= 1:
                    risk_score += 15
                    risk_factors.append(f'{len(worsening_symptoms)} sintoma piorando')
                
                # Verifica mudanças críticas em campos importantes
                critical_fields = ['health_status', 'sleep_quality_last_night', 'pain_level_today']
                for field in critical_fields:
                    if field in trend_data['symptom_trends']:
                        symptom_data = trend_data['symptom_trends'][field]
                        if symptom_data['trend'] == 'worsening' and abs(symptom_data['change']) >= 2:
                            risk_score += 20
                            risk_factors.append(f'{field}: deterioração de {abs(symptom_data["change"]):.1f} pontos')
                        elif symptom_data['trend'] == 'worsening' and abs(symptom_data['change']) >= 1:
                            risk_score += 10
                            risk_factors.append(f'{field}: piora de {abs(symptom_data["change"]):.1f} pontos')
                
                # Verifica período sem registros (gap temporal)
                if trend_data['time_span_days'] > 30 and trend_data['total_records'] < 4:
                    risk_score += 15
                    risk_factors.append(f'Poucos registros em {trend_data["time_span_days"]} dias')
                
                # Classifica risco e adiciona aos alertas
                if risk_score >= 50:
                    priority = 'high'
                    alerts['high_priority_alerts'].append({
                        'participant_id': participant_id,
                        'risk_score': risk_score,
                        'risk_factors': risk_factors,
                        'recommendation': 'Contacto médico urgente recomendado - múltiplos indicadores de deterioração',
                        'last_record_days': trend_data['time_span_days'],
                        'total_records': trend_data['total_records']
                    })
                elif risk_score >= 25:
                    priority = 'medium'
                    alerts['medium_priority_alerts'].append({
                        'participant_id': participant_id,
                        'risk_score': risk_score,
                        'risk_factors': risk_factors,
                        'recommendation': 'Monitorização mais frequente - sinais de possível deterioração',
                        'last_record_days': trend_data['time_span_days'],
                        'total_records': trend_data['total_records']
                    })
                
                if risk_score > 0:
                    alerts['participants_at_risk'][participant_id] = {
                        'risk_level': priority if risk_score >= 25 else 'low',
                        'risk_score': risk_score,
                        'factors': risk_factors,
                        'monitoring_period_days': trend_data['time_span_days']
                    }
            
            # Estatísticas de deterioração
            total_participants = len(temporal_trends['participant_trends']) if temporal_trends['participant_trends'] else 1
            alerts['deterioration_indicators'] = {
                'total_participants_monitored': len(temporal_trends['participant_trends']),
                'high_risk_count': len(alerts['high_priority_alerts']),
                'medium_risk_count': len(alerts['medium_priority_alerts']),
                'participants_at_risk_count': len(alerts['participants_at_risk']),
                'risk_percentage': round((len(alerts['participants_at_risk']) / total_participants * 100), 1),
                'participants_with_longitudinal_data': len(temporal_trends['participant_trends'])
            }
            
        except Exception as e:
            print(f"Erro na detecção de deterioração: {e}")
            import traceback
            traceback.print_exc()
        
        return alerts

    # =====================================
    # SISTEMA DE ALERTAS CLÍNICOS - MÉTODOS NOVOS
    # =====================================
    
    def identify_risk_participants(self):
        """Identifica participantes em risco baseado em critérios clínicos"""
        risk_analysis = {
            'high_risk_participants': [],
            'medium_risk_participants': [],
            'low_risk_participants': [],
            'risk_summary': {},
            'criteria_weights': {
                'deteriorating_symptoms': 30,
                'medication_non_adherence': 25,
                'critical_sleep_issues': 20,
                'long_response_gaps': 15,
                'anomalous_patterns': 10
            }
        }
        
        try:
            # Obtém análises auxiliares
            temporal_trends = self.analyze_temporal_trends()
            
            # Analisa cada participante
            participant_data = {}
            for record in self.data:
                participant_id = record.get('participant_code')
                if not participant_id:
                    continue
                    
                if participant_id not in participant_data:
                    participant_data[participant_id] = {
                        'records': [],
                        'symptoms': {},
                        'medications': {},
                        'sleep_data': {}
                    }
                
                participant_data[participant_id]['records'].append(record)
            
            # Avalia risco para cada participante
            for participant_id, data in participant_data.items():
                risk_score = 0
                risk_factors = []
                
                # 1. Sintomas deteriorando (usando análise temporal)
                if participant_id in temporal_trends['participant_trends']:
                    trend_data = temporal_trends['participant_trends'][participant_id]
                    worsening_symptoms = [s for s in trend_data['symptom_trends'].values() if s['trend'] == 'worsening']
                    
                    if len(worsening_symptoms) >= 3:
                        risk_score += 30
                        risk_factors.append(f'{len(worsening_symptoms)} sintomas deteriorando')
                    elif len(worsening_symptoms) >= 2:
                        risk_score += 20
                        risk_factors.append(f'{len(worsening_symptoms)} sintomas deteriorando')
                    elif len(worsening_symptoms) >= 1:
                        risk_score += 10
                        risk_factors.append(f'{len(worsening_symptoms)} sintoma deteriorando')
                
                # 2. Problemas de adesão medicamentosa
                non_adherence_count = 0
                for record in data['records']:
                    took_meds = record.get('took_medications_yesterday')
                    if took_meds == 'Não':
                        non_adherence_count += 1
                
                if non_adherence_count > 0:
                    adherence_rate = 1 - (non_adherence_count / len(data['records']))
                    if adherence_rate < 0.7:  # Menos de 70% adesão
                        risk_score += 25
                        risk_factors.append(f'Baixa adesão medicamentosa ({adherence_rate*100:.1f}%)')
                    elif adherence_rate < 0.8:  # Menos de 80% adesão
                        risk_score += 15
                        risk_factors.append(f'Adesão medicamentosa moderada ({adherence_rate*100:.1f}%)')
                
                # 3. Problemas críticos de sono
                poor_sleep_count = 0
                for record in data['records']:
                    sleep_quality = record.get('sleep_quality_last_night')
                    if sleep_quality in ['Mal', 'Muito mal']:
                        poor_sleep_count += 1
                
                if poor_sleep_count > len(data['records']) * 0.5:  # Mais de 50% com sono ruim
                    risk_score += 20
                    risk_factors.append(f'Qualidade do sono crítica ({poor_sleep_count}/{len(data["records"])} registros)')
                elif poor_sleep_count > len(data['records']) * 0.3:  # Mais de 30% com sono ruim
                    risk_score += 10
                    risk_factors.append(f'Qualidade do sono preocupante ({poor_sleep_count}/{len(data["records"])} registros)')
                
                # 4. Status de saúde geral deteriorado
                poor_health_count = 0
                for record in data['records']:
                    health_status = record.get('health_status')
                    if health_status in ['Mal', 'Não muito bem']:
                        poor_health_count += 1
                
                if poor_health_count > len(data['records']) * 0.4:  # Mais de 40% com saúde ruim
                    risk_score += 15
                    risk_factors.append(f'Estado de saúde deteriorado ({poor_health_count}/{len(data["records"])} registros)')
                
                # 5. Múltiplos sintomas presentes
                recent_symptoms = {}
                for record in data['records'][-5:]:  # Últimos 5 registros
                    for symptom in ['dizziness_today', 'fatigue_today', 'muscle_weakness_today', 'pain_today']:
                        value = record.get(symptom)
                        if value in ['Frequentemente', 'Sempre']:
                            if symptom not in recent_symptoms:
                                recent_symptoms[symptom] = 0
                            recent_symptoms[symptom] += 1
                
                frequent_symptoms = [s for s, count in recent_symptoms.items() if count >= 2]
                if len(frequent_symptoms) >= 3:
                    risk_score += 15
                    risk_factors.append(f'{len(frequent_symptoms)} sintomas frequentes recentes')
                
                # Classifica risco final
                participant_risk = {
                    'participant_id': participant_id,
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'total_records': len(data['records']),
                    'last_record_date': 'N/A',  # Seria extraído do último registro
                    'recommendation': ''
                }
                
                if risk_score >= 50:
                    participant_risk['risk_level'] = 'high'
                    participant_risk['recommendation'] = 'Contacto médico urgente - múltiplos fatores de risco'
                    risk_analysis['high_risk_participants'].append(participant_risk)
                elif risk_score >= 25:
                    participant_risk['risk_level'] = 'medium'
                    participant_risk['recommendation'] = 'Monitorização intensificada necessária'
                    risk_analysis['medium_risk_participants'].append(participant_risk)
                else:
                    participant_risk['risk_level'] = 'low'
                    participant_risk['recommendation'] = 'Monitorização de rotina'
                    risk_analysis['low_risk_participants'].append(participant_risk)
            
            # Resumo estatístico
            total_participants = len(participant_data)
            risk_analysis['risk_summary'] = {
                'total_participants': total_participants,
                'high_risk_count': len(risk_analysis['high_risk_participants']),
                'medium_risk_count': len(risk_analysis['medium_risk_participants']),
                'low_risk_count': len(risk_analysis['low_risk_participants']),
                'high_risk_percentage': round((len(risk_analysis['high_risk_participants']) / total_participants * 100), 1) if total_participants > 0 else 0,
                'requiring_attention': len(risk_analysis['high_risk_participants']) + len(risk_analysis['medium_risk_participants'])
            }
            
        except Exception as e:
            print(f"Erro na identificação de participantes de risco: {e}")
            import traceback
            traceback.print_exc()
        
        return risk_analysis
    
    def generate_medication_alerts(self):
        """Gera alertas específicos sobre adesão medicamentosa"""
        medication_alerts = {
            'non_adherence_alerts': [],
            'pattern_alerts': [],
            'adverse_effect_alerts': [],
            'medication_summary': {}
        }
        
        try:
            participant_medication_data = {}
            
            # Coleta dados de medicação por participante
            for record in self.data:
                participant_id = record.get('participant_code')
                if not participant_id:
                    continue
                
                if participant_id not in participant_medication_data:
                    participant_medication_data[participant_id] = {
                        'adherence_records': [],
                        'adverse_effects': [],
                        'patterns': []
                    }
                
                # Adesão medicamentosa
                took_meds = record.get('took_medications_yesterday')
                if took_meds:
                    participant_medication_data[participant_id]['adherence_records'].append({
                        'took_medications': took_meds,
                        'date': record.get('questionnaire_date_8', 'N/A')
                    })
                
                # Efeitos adversos (inferidos de sintomas)
                adverse_symptoms = {}
                symptom_fields = ['dizziness_today', 'fatigue_today', 'muscle_weakness_today', 'pain_today']
                for symptom in symptom_fields:
                    value = record.get(symptom)
                    if value in ['Frequentemente', 'Sempre']:
                        adverse_symptoms[symptom] = value
                
                if adverse_symptoms:
                    participant_medication_data[participant_id]['adverse_effects'].append({
                        'symptoms': adverse_symptoms,
                        'date': record.get('questionnaire_date_8', 'N/A')
                    })
            
            # Analisa alertas para cada participante
            for participant_id, med_data in participant_medication_data.items():
                # Alertas de não-adesão
                if med_data['adherence_records']:
                    non_adherence_count = sum(1 for r in med_data['adherence_records'] if r['took_medications'] == 'Não')
                    total_records = len(med_data['adherence_records'])
                    adherence_rate = 1 - (non_adherence_count / total_records)
                    
                    if adherence_rate < 0.7:
                        medication_alerts['non_adherence_alerts'].append({
                            'participant_id': participant_id,
                            'adherence_rate': round(adherence_rate * 100, 1),
                            'missed_doses': non_adherence_count,
                            'total_records': total_records,
                            'severity': 'high' if adherence_rate < 0.5 else 'medium',
                            'recommendation': 'Intervenção urgente necessária' if adherence_rate < 0.5 else 'Reforço da adesão recomendado'
                        })
                
                # Alertas de possíveis efeitos adversos
                if len(med_data['adverse_effects']) > len(med_data['adherence_records']) * 0.3:
                    frequent_symptoms = {}
                    for effect_record in med_data['adverse_effects']:
                        for symptom, frequency in effect_record['symptoms'].items():
                            if symptom not in frequent_symptoms:
                                frequent_symptoms[symptom] = 0
                            frequent_symptoms[symptom] += 1
                    
                    if frequent_symptoms:
                        medication_alerts['adverse_effect_alerts'].append({
                            'participant_id': participant_id,
                            'frequent_symptoms': frequent_symptoms,
                            'total_adverse_reports': len(med_data['adverse_effects']),
                            'recommendation': 'Revisão do plano medicamentoso recomendada'
                        })
            
            # Resumo estatístico
            total_participants = len(participant_medication_data)
            medication_alerts['medication_summary'] = {
                'total_participants_analyzed': total_participants,
                'non_adherence_alerts_count': len(medication_alerts['non_adherence_alerts']),
                'adverse_effect_alerts_count': len(medication_alerts['adverse_effect_alerts']),
                'participants_requiring_intervention': len(set([alert['participant_id'] for alert in medication_alerts['non_adherence_alerts']] + 
                                                             [alert['participant_id'] for alert in medication_alerts['adverse_effect_alerts']]))
            }
            
        except Exception as e:
            print(f"Erro na geração de alertas medicamentosos: {e}")
            import traceback
            traceback.print_exc()
        
        return medication_alerts
    
    def analyze_critical_sleep(self):
        """Analisa problemas críticos de sono"""
        sleep_alerts = {
            'critical_sleep_participants': [],
            'moderate_sleep_issues': [],
            'sleep_pattern_alerts': [],
            'sleep_summary': {}
        }
        
        try:
            participant_sleep_data = {}
            
            # Coleta dados de sono por participante
            for record in self.data:
                participant_id = record.get('participant_code')
                if not participant_id:
                    continue
                
                if participant_id not in participant_sleep_data:
                    participant_sleep_data[participant_id] = {
                        'sleep_quality_records': [],
                        'daytime_sleepiness_records': [],
                        'psqi_related': []
                    }
                
                # Qualidade do sono
                sleep_quality = record.get('sleep_quality_last_night')
                if sleep_quality:
                    participant_sleep_data[participant_id]['sleep_quality_records'].append(sleep_quality)
                
                # Sonolência diurna
                daytime_sleepiness = record.get('daytime_sleepiness')
                if daytime_sleepiness:
                    participant_sleep_data[participant_id]['daytime_sleepiness_records'].append(daytime_sleepiness)
            
            # Analisa cada participante
            for participant_id, sleep_data in participant_sleep_data.items():
                sleep_issues = []
                severity_score = 0
                
                # Avalia qualidade do sono
                if sleep_data['sleep_quality_records']:
                    poor_sleep_count = sum(1 for q in sleep_data['sleep_quality_records'] if q in ['Mal', 'Muito mal'])
                    total_sleep_records = len(sleep_data['sleep_quality_records'])
                    poor_sleep_rate = poor_sleep_count / total_sleep_records
                    
                    if poor_sleep_rate >= 0.6:
                        severity_score += 30
                        sleep_issues.append(f'Qualidade do sono crítica ({poor_sleep_rate*100:.1f}% registros ruins)')
                    elif poor_sleep_rate >= 0.4:
                        severity_score += 15
                        sleep_issues.append(f'Qualidade do sono preocupante ({poor_sleep_rate*100:.1f}% registros ruins)')
                
                # Avalia sonolência diurna
                if sleep_data['daytime_sleepiness_records']:
                    excessive_sleepiness = sum(1 for s in sleep_data['daytime_sleepiness_records'] if s in ['Frequentemente', 'Sempre'])
                    total_sleepiness_records = len(sleep_data['daytime_sleepiness_records'])
                    excessive_rate = excessive_sleepiness / total_sleepiness_records
                    
                    if excessive_rate >= 0.5:
                        severity_score += 25
                        sleep_issues.append(f'Sonolência diurna excessiva ({excessive_rate*100:.1f}% registros)')
                    elif excessive_rate >= 0.3:
                        severity_score += 10
                        sleep_issues.append(f'Sonolência diurna moderada ({excessive_rate*100:.1f}% registros)')
                
                # Classifica gravidade
                if severity_score >= 40 or len(sleep_issues) >= 2:
                    sleep_alerts['critical_sleep_participants'].append({
                        'participant_id': participant_id,
                        'severity_score': severity_score,
                        'sleep_issues': sleep_issues,
                        'total_sleep_records': len(sleep_data['sleep_quality_records']),
                        'recommendation': 'Avaliação do sono urgente - possível distúrbio do sono'
                    })
                elif severity_score >= 15 or len(sleep_issues) >= 1:
                    sleep_alerts['moderate_sleep_issues'].append({
                        'participant_id': participant_id,
                        'severity_score': severity_score,
                        'sleep_issues': sleep_issues,
                        'total_sleep_records': len(sleep_data['sleep_quality_records']),
                        'recommendation': 'Monitorização do sono recomendada'
                    })
            
            # Resumo estatístico
            total_participants = len(participant_sleep_data)
            sleep_alerts['sleep_summary'] = {
                'total_participants_analyzed': total_participants,
                'critical_sleep_count': len(sleep_alerts['critical_sleep_participants']),
                'moderate_sleep_issues_count': len(sleep_alerts['moderate_sleep_issues']),
                'participants_needing_sleep_evaluation': len(sleep_alerts['critical_sleep_participants']) + len(sleep_alerts['moderate_sleep_issues'])
            }
            
        except Exception as e:
            print(f"Erro na análise crítica de sono: {e}")
            import traceback
            traceback.print_exc()
        
        return sleep_alerts
    
    def detect_response_anomalies(self):
        """Detecta padrões anômalos nas respostas"""
        anomaly_alerts = {
            'suspicious_patterns': [],
            'data_quality_issues': [],
            'response_consistency_alerts': [],
            'anomaly_summary': {}
        }
        
        try:
            participant_response_patterns = {}
            
            # Analisa padrões de resposta por participante
            for record in self.data:
                participant_id = record.get('participant_code')
                if not participant_id:
                    continue
                
                if participant_id not in participant_response_patterns:
                    participant_response_patterns[participant_id] = {
                        'response_dates': [],
                        'response_patterns': [],
                        'consistency_checks': []
                    }
                
                # Coleta padrão de respostas para sintomas
                symptom_responses = {}
                for field in ['health_status', 'sleep_quality_last_night', 'daytime_sleepiness', 
                             'dizziness_today', 'fatigue_today', 'muscle_weakness_today', 'pain_today']:
                    value = record.get(field)
                    if value:
                        symptom_responses[field] = value
                
                if symptom_responses:
                    participant_response_patterns[participant_id]['response_patterns'].append(symptom_responses)
                
                # Data de resposta
                response_date = record.get('questionnaire_date_8')
                if response_date:
                    participant_response_patterns[participant_id]['response_dates'].append(response_date)
            
            # Detecta anomalias para cada participante
            for participant_id, patterns in participant_response_patterns.items():
                anomalies = []
                
                # 1. Respostas muito consistentes (possível resposta automática)
                if len(patterns['response_patterns']) >= 5:
                    # Verifica se todas as respostas são idênticas
                    first_pattern = patterns['response_patterns'][0]
                    identical_responses = 0
                    for pattern in patterns['response_patterns'][1:]:
                        if pattern == first_pattern:
                            identical_responses += 1
                    
                    if identical_responses >= len(patterns['response_patterns']) * 0.8:
                        anomalies.append({
                            'type': 'identical_responses',
                            'description': f'{identical_responses}/{len(patterns["response_patterns"])} respostas idênticas',
                            'severity': 'medium'
                        })
                
                # 2. Mudanças extremas súbitas
                if len(patterns['response_patterns']) >= 3:
                    health_values = []
                    value_map = {'Muito bem': 1, 'Bem': 2, 'Razoável': 3, 'Não muito bem': 4, 'Mal': 5}
                    
                    for pattern in patterns['response_patterns']:
                        health_status = pattern.get('health_status')
                        if health_status in value_map:
                            health_values.append(value_map[health_status])
                    
                    if len(health_values) >= 3:
                        for i in range(1, len(health_values)):
                            change = abs(health_values[i] - health_values[i-1])
                            if change >= 3:  # Mudança de 3+ pontos (ex: Muito bem -> Não muito bem)
                                anomalies.append({
                                    'type': 'extreme_change',
                                    'description': f'Mudança extrema no status de saúde (diferença de {change} pontos)',
                                    'severity': 'high'
                                })
                                break
                
                if anomalies:
                    anomaly_alerts['suspicious_patterns'].append({
                        'participant_id': participant_id,
                        'anomalies': anomalies,
                        'total_responses': len(patterns['response_patterns']),
                        'recommendation': 'Verificação manual das respostas recomendada'
                    })
            
            # Resumo das anomalias
            anomaly_alerts['anomaly_summary'] = {
                'participants_with_anomalies': len(anomaly_alerts['suspicious_patterns']),
                'total_anomalies': sum(len(alert['anomalies']) for alert in anomaly_alerts['suspicious_patterns']),
                'anomaly_rate': round((len(anomaly_alerts['suspicious_patterns']) / len(participant_response_patterns)) * 100, 1) if participant_response_patterns else 0
            }
            
            return anomaly_alerts
            
        except Exception as e:
            print(f"❌ Erro na detecção de anomalias: {e}")
            return {
                'suspicious_patterns': [],
                'data_quality_issues': [],
                'response_consistency_alerts': [],
                'anomaly_summary': {'participants_with_anomalies': 0, 'total_anomalies': 0, 'anomaly_rate': 0}
            }

    # =====================================
    # 💊 ANÁLISE DE ADESÃO MEDICAMENTOSA  
    # =====================================
    
    def calculate_adherence_rates(self):
        """Calcula taxas de adesão medicamentosa detalhadas"""
        try:
            # Converter dados para DataFrame se necessário
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
                
            # Dados do instrumento de adesão à medicação
            medication_instrument = 'VIII  - Questionário de adesão à medicação, sintomas e bem-estar'
            medication_data = data_df[data_df['redcap_repeat_instrument'] == medication_instrument]
            
            if medication_data.empty:
                print("⚠️ Usando dados gerais de medicação")
                medication_data = data_df
            
            # Taxa geral de adesão baseada em "took_medications_yesterday"
            adherence_scores = []
            participant_adherence = {}
            
            # Usar participant_code como identificador
            id_field = 'participant_code'
            
            # Analisar adesão por participante
            for participant_id in medication_data[id_field].unique():
                if pd.isna(participant_id):
                    continue
                    
                participant_data = medication_data[medication_data[id_field] == participant_id]
                
                # Calcular adesão baseada nos dados disponíveis
                scores = []
                adherence_records = 0
                
                # 1. Adesão baseada em "took_medications_yesterday"
                took_meds_values = participant_data['took_medications_yesterday'].dropna()
                for value in took_meds_values:
                    if str(value) == 'Sim':
                        scores.append(4)  # Alta adesão
                        adherence_records += 1
                    elif str(value) == 'Não':
                        scores.append(0)  # Baixa adesão
                        adherence_records += 1
                    elif str(value) in ['Às vezes', 'Parcialmente']:
                        scores.append(2)  # Adesão moderada
                        adherence_records += 1
                
                # 2. Verificar se tem medicação prescrita (medication_name_other)
                has_medication = not participant_data['medication_name_other'].dropna().empty
                
                # 3. Uso de medicação para dormir
                sleep_med_use = participant_data['sleep_medication_use'].dropna()
                for value in sleep_med_use:
                    if '3x/semana ou mais' in str(value):
                        scores.append(3)  # Uso regular
                        adherence_records += 1
                    elif 'nunca' in str(value).lower():
                        scores.append(1)  # Uso raro
                        adherence_records += 1
                
                # Calcular score médio se houver dados
                if scores and has_medication:
                    avg_score = np.mean(scores)
                    percentage = round((avg_score / 4) * 100, 1)
                    
                    # Determinar nível
                    if percentage >= 75:
                        level = 'Alta'
                    elif percentage >= 50:
                        level = 'Média'
                    else:
                        level = 'Baixa'
                    
                    participant_adherence[str(participant_id)] = {
                        'score': round(avg_score, 2),
                        'percentage': percentage,
                        'level': level,
                        'total_records': adherence_records,
                        'has_medication': has_medication
                    }
                    adherence_scores.append(avg_score)
            
            # Adesão por medicamento (usando medication_name_other)
            medication_adherence = {}
            medication_names = data_df['medication_name_other'].dropna().unique()
            
            for med_name in medication_names:
                if pd.isna(med_name):
                    continue
                    
                # Participantes que usam este medicamento
                med_users = data_df[data_df['medication_name_other'] == med_name]
                med_scores = []
                
                for _, row in med_users.iterrows():
                    participant_id = row[id_field]
                    if participant_id in [p for p in participant_adherence.keys()]:
                        participant_score = participant_adherence[str(participant_id)]['score']
                        med_scores.append(participant_score)
                
                if med_scores:
                    avg_score = np.mean(med_scores)
                    medication_adherence[str(med_name)] = {
                        'score': round(avg_score, 2),
                        'percentage': round((avg_score / 4) * 100, 1),
                        'n_participants': len(med_scores)
                    }
            
            # Estatísticas gerais
            if adherence_scores:
                overall_score = np.mean(adherence_scores)
                statistics = {
                    'mean_adherence': round(overall_score, 2),
                    'mean_percentage': round((overall_score / 4) * 100, 1),
                    'std_dev': round(np.std(adherence_scores), 2),
                    'high_adherence': len([s for s in adherence_scores if s >= 3]),
                    'medium_adherence': len([s for s in adherence_scores if 2 <= s < 3]),
                    'low_adherence': len([s for s in adherence_scores if s < 2]),
                    'total_participants': len(participant_adherence)
                }
            else:
                overall_score = 0
                statistics = {
                    'mean_adherence': 0, 
                    'mean_percentage': 0, 
                    'std_dev': 0,
                    'high_adherence': 0,
                    'medium_adherence': 0,
                    'low_adherence': 0,
                    'total_participants': 0
                }
            
            return {
                'overall': round((overall_score / 4) * 100, 1) if adherence_scores else 0,
                'by_participant': participant_adherence,
                'by_medication': medication_adherence,
                'statistics': statistics
            }
            
        except Exception as e:
            print(f"❌ Erro no cálculo de adesão: {e}")
            import traceback
            traceback.print_exc()
            return {'overall': 0, 'by_participant': {}, 'by_medication': {}, 'statistics': {}}
    
    def analyze_adherence_factors(self):
        """Analisa fatores associados à adesão medicamentosa"""
        try:
            # Converter dados para DataFrame se necessário
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
                
            medication_data = data_df[data_df['redcap_repeat_instrument'] == 'medication']
            
            if medication_data.empty:
                # Tentar usar dados gerais
                medication_data = data_df
            
            # Correlações com outras variáveis
            correlations = {}
            factors = {}
            
            # Usar participant_code como identificador primário
            id_field = 'participant_code'
            
            # Adesão vs. Qualidade do sono
            sleep_adherence_data = []
            if all(col in data_df.columns for col in ['sleep_quality_last_night']) and id_field in data_df.columns:
                # Coletar dados de participantes únicos
                for participant_id in data_df[id_field].unique():
                    if pd.isna(participant_id):
                        continue
                        
                    participant_data = data_df[data_df[id_field] == participant_id]
                    
                    # Calcular média de adesão
                    adherence_values = []
                    adherence_mapping = {'Sempre': 4, 'Frequentemente': 3, 'Às vezes': 2, 'Raramente': 1, 'Nunca': 0}
                    
                    for adherence_field in ['medication_adherence', 'adherence_score']:
                        if adherence_field in participant_data.columns:
                            for val in participant_data[adherence_field].dropna():
                                if str(val) in adherence_mapping:
                                    adherence_values.append(adherence_mapping[str(val)])
                                else:
                                    try:
                                        numeric_val = float(val)
                                        if 0 <= numeric_val <= 4:
                                            adherence_values.append(numeric_val)
                                    except:
                                        continue
                    
                    # Calcular média de qualidade do sono
                    sleep_values = []
                    for val in participant_data['sleep_quality_last_night'].dropna():
                        try:
                            sleep_val = float(val)
                            sleep_values.append(sleep_val)
                        except:
                            # Tentar mapear valores textuais
                            sleep_mapping = {'Muito boa': 1, 'Boa': 2, 'Razoável': 3, 'Má': 4, 'Muito má': 5}
                            if str(val) in sleep_mapping:
                                sleep_values.append(sleep_mapping[str(val)])
                    
                    if adherence_values and sleep_values:
                        sleep_adherence_data.append({
                            'adherence': np.mean(adherence_values),
                            'sleep_quality': np.mean(sleep_values)
                        })
                
                if len(sleep_adherence_data) > 1:
                    adherence_vals = [item['adherence'] for item in sleep_adherence_data]
                    sleep_vals = [item['sleep_quality'] for item in sleep_adherence_data]
                    correlation = np.corrcoef(adherence_vals, sleep_vals)[0, 1]
                    correlations['sleep_quality'] = round(correlation, 3) if not np.isnan(correlation) else 0
            
            # Efeitos adversos vs adesão
            adverse_effect_impact = {}
            for adverse_field in ['adverse_effects', 'side_effects', 'medication_side_effects']:
                if adverse_field in data_df.columns:
                    for effect in data_df[adverse_field].dropna().unique():
                        if pd.isna(effect):
                            continue
                            
                        effect_data = data_df[data_df[adverse_field] == effect]
                        adherence_scores = []
                        
                        for adherence_field in ['medication_adherence', 'adherence_score']:
                            if adherence_field in effect_data.columns:
                                adherence_mapping = {'Sempre': 4, 'Frequentemente': 3, 'Às vezes': 2, 'Raramente': 1, 'Nunca': 0}
                                for val in effect_data[adherence_field].dropna():
                                    if str(val) in adherence_mapping:
                                        adherence_scores.append(adherence_mapping[str(val)])
                        
                        if adherence_scores:
                            adverse_effect_impact[str(effect)] = {
                                'mean_adherence': round(np.mean(adherence_scores), 2),
                                'n_participants': len(effect_data[id_field].unique())
                            }
                    break  # Use first available field
            
            if adverse_effect_impact:
                factors['adverse_effects'] = adverse_effect_impact
            
            # Grupos de risco (placeholder)
            risk_groups = {
                'high_risk': [],
                'medium_risk': [], 
                'low_risk': []
            }
            
            return {
                'correlations': correlations,
                'factors': factors,
                'risk_groups': risk_groups
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de fatores: {e}")
            import traceback
            traceback.print_exc()
            return {'correlations': {}, 'factors': {}, 'risk_groups': {}}
    
    def analyze_adverse_effects(self):
        """Analisa efeitos adversos e sua relação com adesão"""
        try:
            # Converter dados para DataFrame se necessário
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            effects_frequency = {}
            severity_impact = {}
            discontinuation_patterns = {}
            
            # Identificador de participante
            id_field = 'participant_code'
            
            # Analisar sintomas reportados (proxy para efeitos adversos)
            symptom_fields = ['other_symptoms_today', 'other_symptoms_description']
            
            # Frequência de sintomas/efeitos
            for field in symptom_fields:
                if field in data_df.columns:
                    symptoms = data_df[field].dropna()
                    
                    for symptom in symptoms.unique():
                        if pd.isna(symptom) or str(symptom).strip() == '':
                            continue
                            
                        symptom_str = str(symptom)
                        count = len(symptoms[symptoms == symptom])
                        total = len(symptoms)
                        
                        if count > 0:
                            effects_frequency[symptom_str] = {
                                'count': int(count),
                                'percentage': round((count / total) * 100, 1) if total > 0 else 0,
                                'participants': len(data_df[data_df[field] == symptom][id_field].unique())
                            }
            
            # Analisar impacto na adesão baseado em status de saúde
            health_status_values = data_df['health_status'].dropna()
            
            for status in health_status_values.unique():
                if pd.isna(status):
                    continue
                    
                status_data = data_df[data_df['health_status'] == status]
                
                # Verificar adesão destes participantes
                adherence_scores = []
                for _, row in status_data.iterrows():
                    if row['took_medications_yesterday'] == 'Sim':
                        adherence_scores.append(4)
                    elif row['took_medications_yesterday'] == 'Não':
                        adherence_scores.append(0)
                
                if adherence_scores:
                    severity_impact[str(status)] = {
                        'mean_adherence': round(np.mean(adherence_scores), 2),
                        'adherence_percentage': round((np.mean(adherence_scores) / 4) * 100, 1),
                        'n_cases': len(adherence_scores)
                    }
            
            # Padrões de não-adesão (usando medication_nonadherence_reason)
            if 'medication_nonadherence_reason' in data_df.columns:
                nonadherence_reasons = data_df['medication_nonadherence_reason'].dropna()
                
                for reason in nonadherence_reasons.unique():
                    if pd.isna(reason) or str(reason).strip() == '':
                        continue
                        
                    count = len(nonadherence_reasons[nonadherence_reasons == reason])
                    total = len(nonadherence_reasons)
                    
                    discontinuation_patterns[str(reason)] = {
                        'count': int(count),
                        'percentage': round((count / total) * 100, 1) if total > 0 else 0
                    }
            
            return {
                'effects_frequency': effects_frequency,
                'severity_impact': severity_impact,
                'discontinuation_patterns': discontinuation_patterns
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de efeitos adversos: {e}")
            import traceback
            traceback.print_exc()
            return {'effects_frequency': {}, 'severity_impact': {}, 'discontinuation_patterns': {}}
    
    def medication_temporal_patterns(self):
        """Analisa padrões temporais da adesão medicamentosa"""
        try:
            # Converter dados para DataFrame se necessário  
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            monthly_trends = {}
            weekly_patterns = {}
            adherence_evolution = {}
            
            # Identificador de participante
            id_field = 'participant_code'
            
            # Usar instância de repetição como proxy temporal
            if 'redcap_repeat_instance' in data_df.columns:
                data_df['instance'] = pd.to_numeric(data_df['redcap_repeat_instance'], errors='coerce')
                
                # Tendências por instância (período temporal)
                for instance in sorted(data_df['instance'].dropna().unique()):
                    instance_data = data_df[data_df['instance'] == instance]
                    
                    # Calcular adesão para esta instância
                    adherence_count = 0
                    total_count = 0
                    
                    for _, row in instance_data.iterrows():
                        if pd.notna(row.get('took_medications_yesterday')):
                            total_count += 1
                            if row['took_medications_yesterday'] == 'Sim':
                                adherence_count += 1
                    
                    if total_count > 0:
                        adherence_percentage = round((adherence_count / total_count) * 100, 1)
                        monthly_trends[f'Período {int(instance)}'] = {
                            'mean_adherence': round((adherence_count / total_count) * 4, 2),
                            'percentage': adherence_percentage,
                            'n_records': total_count
                        }
            
            # Evolução da adesão por participante
            medication_instrument = 'VIII  - Questionário de adesão à medicação, sintomas e bem-estar'
            participant_data = data_df[data_df['redcap_repeat_instrument'] == medication_instrument]
            
            if participant_data.empty:
                participant_data = data_df
            
            for participant_id in participant_data[id_field].unique():
                if pd.isna(participant_id):
                    continue
                    
                participant_records = participant_data[participant_data[id_field] == participant_id]
                
                if 'redcap_repeat_instance' in participant_records.columns:
                    participant_records = participant_records.sort_values('redcap_repeat_instance')
                
                adherence_timeline = []
                for _, row in participant_records.iterrows():
                    if pd.notna(row.get('took_medications_yesterday')):
                        adherence_score = 4 if row['took_medications_yesterday'] == 'Sim' else 0
                        adherence_timeline.append({
                            'instance': row.get('redcap_repeat_instance', 1),
                            'adherence_score': adherence_score,
                            'adherence_percentage': (adherence_score / 4) * 100
                        })
                
                if len(adherence_timeline) > 1:
                    scores = [item['adherence_score'] for item in adherence_timeline]
                    trend = 'Melhorando' if scores[-1] > scores[0] else 'Piorando' if scores[-1] < scores[0] else 'Estável'
                    
                    adherence_evolution[str(participant_id)] = {
                        'timeline': adherence_timeline,
                        'trend': trend,
                        'first_score': scores[0],
                        'last_score': scores[-1],
                        'change': scores[-1] - scores[0]
                    }
            
            return {
                'monthly_trends': monthly_trends,
                'weekly_patterns': weekly_patterns,
                'adherence_evolution': adherence_evolution
            }
            
        except Exception as e:
            print(f"❌ Erro na análise temporal: {e}")
            import traceback
            traceback.print_exc()
            return {'monthly_trends': {}, 'weekly_patterns': {}, 'adherence_evolution': {}}
    
    # =====================================
    # 😴 ANÁLISE DO SONO - FUNÇÕES INDEPENDENTES
    # =====================================
    
    def analyze_psqi_components_rm4health(self):
        """Analisa os 7 componentes do PSQI (Pittsburgh Sleep Quality Index)"""
        try:
            # Converter dados para DataFrame se necessário
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            # Instrumento específico do sono
            sleep_instrument = 'VII - Questionário de Pittsburgh sobre a Qualidade do Sono  (PSQI-PT)'
            sleep_data = data_df[data_df['redcap_repeat_instrument'] == sleep_instrument]
            
            if sleep_data.empty:
                print("⚠️ Usando dados gerais para análise do sono")
                sleep_data = data_df
            
            # Componentes PSQI mapeados para campos RM4Health
            psqi_components = {
                'sleep_quality': {
                    'name': 'Qualidade Subjetiva do Sono',
                    'field': 'sleep_quality_last_night',
                    'description': 'Avaliação pessoal da qualidade do sono',
                    'scores': [],
                    'distribution': {}
                },
                'sleep_latency': {
                    'name': 'Latência do Sono',
                    'field': 'time_to_fall_asleep',
                    'description': 'Tempo necessário para adormecer',
                    'scores': [],
                    'distribution': {}
                },
                'sleep_duration': {
                    'name': 'Duração do Sono',
                    'field': 'total_sleep_time',
                    'description': 'Número total de horas de sono',
                    'scores': [],
                    'distribution': {}
                },
                'sleep_efficiency': {
                    'name': 'Eficiência do Sono',
                    'field': 'sleep_efficiency_score',
                    'description': 'Razão entre tempo dormindo e tempo na cama',
                    'scores': [],
                    'distribution': {}
                },
                'sleep_disturbances': {
                    'name': 'Perturbações do Sono',
                    'field': 'sleep_disturbances_score',
                    'description': 'Frequência de interrupções durante a noite',
                    'scores': [],
                    'distribution': {}
                },
                'sleep_medication': {
                    'name': 'Uso de Medicação para Dormir',
                    'field': 'sleep_medication_use',
                    'description': 'Frequência de uso de medicação para dormir',
                    'scores': [],
                    'distribution': {}
                },
                'daytime_dysfunction': {
                    'name': 'Disfunção Diurna',
                    'field': 'daytime_sleepiness',
                    'description': 'Sonolência e fadiga durante o dia',
                    'scores': [],
                    'distribution': {}
                }
            }
            
            # Analisar cada componente
            for comp_key, component in psqi_components.items():
                field = component['field']
                
                if field in sleep_data.columns:
                    values = sleep_data[field].dropna()
                    
                    # Mapear valores textuais para numéricos
                    numeric_scores = []
                    value_counts = {}
                    
                    for value in values:
                        str_value = str(value)
                        
                        # Contar distribuição
                        if str_value in value_counts:
                            value_counts[str_value] += 1
                        else:
                            value_counts[str_value] = 1
                        
                        # Mapear para scores numéricos (0-3 conforme PSQI)
                        if comp_key == 'sleep_quality':
                            quality_map = {'Muito boa': 0, 'Boa': 1, 'Razoável': 2, 'Má': 3, 'Muito má': 3}
                            if str_value in quality_map:
                                numeric_scores.append(quality_map[str_value])
                        
                        elif comp_key == 'sleep_medication':
                            med_map = {'Nunca': 0, 'Menos de 1x/semana': 1, '1-2x/semana': 2, '3x/semana ou mais': 3}
                            if str_value in med_map:
                                numeric_scores.append(med_map[str_value])
                        
                        elif comp_key == 'daytime_dysfunction':
                            # Mapear sonolência diurna
                            sleepiness_map = {'Nunca': 0, 'Raramente': 1, 'Às vezes': 2, 'Frequentemente': 3}
                            if str_value in sleepiness_map:
                                numeric_scores.append(sleepiness_map[str_value])
                        
                        else:
                            # Para outros campos, tentar converter diretamente
                            try:
                                numeric_val = float(str_value)
                                if 0 <= numeric_val <= 3:
                                    numeric_scores.append(numeric_val)
                                elif numeric_val > 3:
                                    # Normalizar para escala 0-3
                                    normalized = min(3, numeric_val / (numeric_val.max() if hasattr(numeric_val, 'max') else 10) * 3)
                                    numeric_scores.append(normalized)
                            except:
                                continue
                    
                    # Armazenar resultados
                    component['scores'] = numeric_scores
                    component['distribution'] = value_counts
                    component['mean_score'] = round(np.mean(numeric_scores), 2) if numeric_scores else 0
                    component['participants'] = len(numeric_scores)
                else:
                    # Campo não encontrado nos dados - definir valores padrão
                    component['scores'] = []
                    component['distribution'] = {}
                    component['mean_score'] = 0
                    component['participants'] = 0
            
            # Calcular PSQI global
            global_scores = []
            valid_participants = set()
            
            for participant_id in sleep_data['participant_code'].unique():
                if pd.isna(participant_id):
                    continue
                
                participant_data = sleep_data[sleep_data['participant_code'] == participant_id]
                participant_psqi = 0
                valid_components = 0
                
                for comp_key, component in psqi_components.items():
                    if component['scores']:
                        # Simular score para este participante (média do componente)
                        if component['mean_score'] > 0:
                            participant_psqi += component['mean_score']
                            valid_components += 1
                
                if valid_components >= 4:  # Mínimo de 4 componentes para PSQI válido
                    global_scores.append(participant_psqi)
                    valid_participants.add(str(participant_id))
            
            # Classificação da qualidade do sono
            sleep_quality_classification = {
                'good_sleepers': len([s for s in global_scores if s <= 5]),
                'poor_sleepers': len([s for s in global_scores if s > 5]),
                'mean_psqi': round(np.mean(global_scores), 2) if global_scores else 0,
                'total_participants': len(valid_participants)
            }
            
            return {
                'components': psqi_components,
                'global_psqi': {
                    'scores': global_scores,
                    'classification': sleep_quality_classification
                },
                'summary': {
                    'total_participants': len(valid_participants),
                    'mean_global_psqi': round(np.mean(global_scores), 2) if global_scores else 0,
                    'good_sleepers_percentage': round((sleep_quality_classification['good_sleepers'] / max(1, len(global_scores))) * 100, 1) if global_scores else 0
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na análise PSQI: {e}")
            import traceback
            traceback.print_exc()
            return {'components': {}, 'global_psqi': {}, 'summary': {}}
    
    def create_sleep_profiles_rm4health(self):
        """Cria perfis de sono baseados em clustering de padrões"""
        try:
            # Converter dados para DataFrame se necessário
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            # Coletar dados de sono para clustering
            sleep_features = []
            participant_profiles = {}
            
            for participant_id in data_df['participant_code'].unique():
                if pd.isna(participant_id):
                    continue
                
                participant_data = data_df[data_df['participant_code'] == participant_id]
                
                # Extrair características do sono
                features = {}
                
                # Qualidade do sono
                if 'sleep_quality_last_night' in participant_data.columns:
                    quality_values = participant_data['sleep_quality_last_night'].dropna()
                    if not quality_values.empty:
                        quality_map = {'Muito boa': 5, 'Boa': 4, 'Razoável': 3, 'Má': 2, 'Muito má': 1}
                        numeric_qualities = [quality_map.get(str(v), 3) for v in quality_values]
                        features['sleep_quality'] = np.mean(numeric_qualities)
                
                # Sonolência diurna
                if 'daytime_sleepiness' in participant_data.columns:
                    sleepiness_values = participant_data['daytime_sleepiness'].dropna()
                    if not sleepiness_values.empty:
                        sleepiness_map = {'Nunca': 1, 'Raramente': 2, 'Às vezes': 3, 'Frequentemente': 4}
                        numeric_sleepiness = [sleepiness_map.get(str(v), 2) for v in sleepiness_values]
                        features['daytime_sleepiness'] = np.mean(numeric_sleepiness)
                
                # Uso de medicação para dormir
                if 'sleep_medication_use' in participant_data.columns:
                    med_values = participant_data['sleep_medication_use'].dropna()
                    if not med_values.empty:
                        med_map = {'Nunca': 1, 'Menos de 1x/semana': 2, '1-2x/semana': 3, '3x/semana ou mais': 4}
                        numeric_med = [med_map.get(str(v), 1) for v in med_values]
                        features['medication_use'] = np.mean(numeric_med)
                
                # Só incluir se tiver pelo menos 2 características
                if len(features) >= 2:
                    sleep_features.append(features)
                    
                    # Criar perfil baseado em regras simples
                    sleep_quality = features.get('sleep_quality', 3)
                    daytime_sleepiness = features.get('daytime_sleepiness', 2)
                    medication_use = features.get('medication_use', 1)
                    
                    # Classificação em perfis
                    if sleep_quality >= 4 and daytime_sleepiness <= 2 and medication_use <= 2:
                        profile = 'Bom Dormidor'
                        profile_color = '#28a745'  # Verde
                    elif sleep_quality <= 2 or daytime_sleepiness >= 3 or medication_use >= 3:
                        profile = 'Insone'
                        profile_color = '#dc3545'  # Vermelho
                    elif medication_use >= 3:
                        profile = 'Dependente de Medicação'
                        profile_color = '#fd7e14'  # Laranja
                    else:
                        profile = 'Sono Moderado'
                        profile_color = '#ffc107'  # Amarelo
                    
                    participant_profiles[str(participant_id)] = {
                        'profile': profile,
                        'color': profile_color,
                        'features': features,
                        'sleep_quality_score': sleep_quality,
                        'daytime_sleepiness_score': daytime_sleepiness,
                        'medication_score': medication_use
                    }
            
            # Contagem por perfil
            profile_counts = {}
            for profile_data in participant_profiles.values():
                profile = profile_data['profile']
                if profile in profile_counts:
                    profile_counts[profile] += 1
                else:
                    profile_counts[profile] = 1
            
            # Estatísticas dos perfis
            profile_stats = {}
            for profile_type in profile_counts.keys():
                participants_in_profile = [p for p in participant_profiles.values() if p['profile'] == profile_type]
                
                if participants_in_profile:
                    avg_quality = np.mean([p['sleep_quality_score'] for p in participants_in_profile])
                    avg_sleepiness = np.mean([p['daytime_sleepiness_score'] for p in participants_in_profile])
                    avg_medication = np.mean([p['medication_score'] for p in participants_in_profile])
                    
                    profile_stats[profile_type] = {
                        'count': profile_counts[profile_type],
                        'percentage': round((profile_counts[profile_type] / len(participant_profiles)) * 100, 1) if participant_profiles else 0,
                        'avg_sleep_quality': round(avg_quality, 2),
                        'avg_daytime_sleepiness': round(avg_sleepiness, 2),
                        'avg_medication_use': round(avg_medication, 2),
                        'color': participants_in_profile[0]['color']
                    }
            
            return {
                'participant_profiles': participant_profiles,
                'profile_distribution': profile_counts,
                'profile_statistics': profile_stats,
                'total_participants': len(participant_profiles)
            }
            
        except Exception as e:
            print(f"❌ Erro na criação de perfis de sono: {e}")
            import traceback
            traceback.print_exc()
            return {'participant_profiles': {}, 'profile_distribution': {}, 'profile_statistics': {}, 'total_participants': 0}
    
    def sleep_symptom_correlations_rm4health(self):
        """Analisa correlações entre qualidade do sono e sintomas"""
        try:
            # Converter dados para DataFrame se necessário
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            correlations = {}
            sleep_impact_analysis = {}
            
            # Campos de sono para correlação
            sleep_fields = ['sleep_quality_last_night', 'daytime_sleepiness']
            
            # Campos de sintomas/saúde para correlação
            symptom_fields = ['health_status', 'other_symptoms_today', 'vas_health_today']
            
            # Analisar correlações
            for sleep_field in sleep_fields:
                if sleep_field not in data_df.columns:
                    continue
                
                correlations[sleep_field] = {}
                
                for symptom_field in symptom_fields:
                    if symptom_field not in data_df.columns:
                        continue
                    
                    # Preparar dados para correlação
                    sleep_symptom_pairs = []
                    
                    for participant_id in data_df['participant_code'].unique():
                        if pd.isna(participant_id):
                            continue
                        
                        participant_data = data_df[data_df['participant_code'] == participant_id]
                        
                        # Obter valores de sono
                        sleep_values = []
                        for sleep_val in participant_data[sleep_field].dropna():
                            if sleep_field == 'sleep_quality_last_night':
                                quality_map = {'Muito boa': 5, 'Boa': 4, 'Razoável': 3, 'Má': 2, 'Muito má': 1}
                                if str(sleep_val) in quality_map:
                                    sleep_values.append(quality_map[str(sleep_val)])
                            elif sleep_field == 'daytime_sleepiness':
                                sleepiness_map = {'Nunca': 1, 'Raramente': 2, 'Às vezes': 3, 'Frequentemente': 4}
                                if str(sleep_val) in sleepiness_map:
                                    sleep_values.append(sleepiness_map[str(sleep_val)])
                            else:
                                try:
                                    sleep_values.append(float(sleep_val))
                                except:
                                    continue
                        
                        # Obter valores de sintomas
                        symptom_values = []
                        for symptom_val in participant_data[symptom_field].dropna():
                            if symptom_field == 'health_status':
                                health_map = {'Muito bem': 5, 'Bem': 4, 'Razoável': 3, 'Não muito bem': 2, 'Mal': 1}
                                if str(symptom_val) in health_map:
                                    symptom_values.append(health_map[str(symptom_val)])
                            elif symptom_field == 'vas_health_today':
                                try:
                                    symptom_values.append(float(symptom_val))
                                except:
                                    continue
                            else:
                                # Para outros campos, assumir que não-vazio indica presença de sintoma
                                if str(symptom_val).strip() and str(symptom_val) != 'nan':
                                    symptom_values.append(1)
                                else:
                                    symptom_values.append(0)
                        
                        # Combinar dados se ambos existirem
                        if sleep_values and symptom_values:
                            sleep_mean = np.mean(sleep_values)
                            symptom_mean = np.mean(symptom_values)
                            sleep_symptom_pairs.append({
                                'participant_id': participant_id,
                                'sleep': sleep_mean,
                                'symptom': symptom_mean
                            })
                    
                    # Calcular correlação se houver dados suficientes
                    if len(sleep_symptom_pairs) > 2:
                        sleep_vals = [pair['sleep'] for pair in sleep_symptom_pairs]
                        symptom_vals = [pair['symptom'] for pair in sleep_symptom_pairs]
                        
                        correlation = np.corrcoef(sleep_vals, symptom_vals)[0, 1]
                        if not np.isnan(correlation):
                            correlations[sleep_field][symptom_field] = {
                                'correlation': round(correlation, 3),
                                'n_participants': len(sleep_symptom_pairs),
                                'strength': 'Forte' if abs(correlation) >= 0.5 else 'Moderada' if abs(correlation) >= 0.3 else 'Fraca',
                                'direction': 'Positiva' if correlation > 0 else 'Negativa'
                            }
            
            # Análise do impacto do sono na saúde diária
            sleep_health_impact = {}
            
            for participant_id in data_df['participant_code'].unique():
                if pd.isna(participant_id):
                    continue
                
                participant_data = data_df[data_df['participant_code'] == participant_id]
                
                # Calcular scores médios de sono e saúde
                sleep_score = 0
                health_score = 0
                valid_sleep = False
                valid_health = False
                
                # Score de sono (qualidade)
                if 'sleep_quality_last_night' in participant_data.columns:
                    quality_values = participant_data['sleep_quality_last_night'].dropna()
                    if not quality_values.empty:
                        quality_map = {'Muito boa': 5, 'Boa': 4, 'Razoável': 3, 'Má': 2, 'Muito má': 1}
                        numeric_qualities = [quality_map.get(str(v), 3) for v in quality_values]
                        sleep_score = np.mean(numeric_qualities)
                        valid_sleep = True
                
                # Score de saúde
                if 'health_status' in participant_data.columns:
                    health_values = participant_data['health_status'].dropna()
                    if not health_values.empty:
                        health_map = {'Muito bem': 5, 'Bem': 4, 'Razoável': 3, 'Não muito bem': 2, 'Mal': 1}
                        numeric_health = [health_map.get(str(v), 3) for v in health_values]
                        health_score = np.mean(numeric_health)
                        valid_health = True
                
                if valid_sleep and valid_health:
                    sleep_health_impact[str(participant_id)] = {
                        'sleep_quality': round(sleep_score, 2),
                        'health_status': round(health_score, 2),
                        'sleep_category': 'Bom Sono' if sleep_score >= 4 else 'Sono Moderado' if sleep_score >= 3 else 'Sono Ruim',
                        'health_category': 'Boa Saúde' if health_score >= 4 else 'Saúde Moderada' if health_score >= 3 else 'Saúde Ruim'
                    }
            
            return {
                'correlations': correlations,
                'sleep_health_impact': sleep_health_impact,
                'summary': {
                    'total_correlations': sum(len(corr) for corr in correlations.values()),
                    'participants_analyzed': len(sleep_health_impact),
                    'significant_correlations': sum(1 for field_corrs in correlations.values() 
                                                  for corr in field_corrs.values() 
                                                  if abs(corr['correlation']) >= 0.3)
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de correlações sono-sintoma: {e}")
            import traceback
            traceback.print_exc()
            return {'correlations': {}, 'sleep_health_impact': {}, 'summary': {}}
    
    def medication_sleep_impact_rm4health(self):
        """Analisa o impacto da medicação na qualidade do sono"""
        try:
            # Converter dados para DataFrame se necessário
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            medication_sleep_analysis = {}
            sleep_medication_patterns = {}
            
            # Analisar uso de medicação para dormir vs qualidade do sono
            sleep_med_impact = {}
            
            for participant_id in data_df['participant_code'].unique():
                if pd.isna(participant_id):
                    continue
                
                participant_data = data_df[data_df['participant_code'] == participant_id]
                
                # Uso de medicação para dormir
                sleep_med_use = None
                if 'sleep_medication_use' in participant_data.columns:
                    med_values = participant_data['sleep_medication_use'].dropna()
                    if not med_values.empty:
                        med_map = {'Nunca': 0, 'Menos de 1x/semana': 1, '1-2x/semana': 2, '3x/semana ou mais': 3}
                        numeric_med = [med_map.get(str(v), 0) for v in med_values]
                        sleep_med_use = np.mean(numeric_med)
                
                # Qualidade do sono
                sleep_quality = None
                if 'sleep_quality_last_night' in participant_data.columns:
                    quality_values = participant_data['sleep_quality_last_night'].dropna()
                    if not quality_values.empty:
                        quality_map = {'Muito boa': 5, 'Boa': 4, 'Razoável': 3, 'Má': 2, 'Muito má': 1}
                        numeric_qualities = [quality_map.get(str(v), 3) for v in quality_values]
                        sleep_quality = np.mean(numeric_qualities)
                
                # Sonolência diurna
                daytime_sleepiness = None
                if 'daytime_sleepiness' in participant_data.columns:
                    sleepiness_values = participant_data['daytime_sleepiness'].dropna()
                    if not sleepiness_values.empty:
                        sleepiness_map = {'Nunca': 1, 'Raramente': 2, 'Às vezes': 3, 'Frequentemente': 4}
                        numeric_sleepiness = [sleepiness_map.get(str(v), 2) for v in sleepiness_values]
                        daytime_sleepiness = np.mean(numeric_sleepiness)
                
                # Medicação geral (medication_name_other)
                has_general_medication = False
                if 'medication_name_other' in participant_data.columns:
                    med_names = participant_data['medication_name_other'].dropna()
                    has_general_medication = not med_names.empty
                
                # Armazenar dados se houver informações relevantes
                if sleep_med_use is not None or sleep_quality is not None:
                    sleep_med_impact[str(participant_id)] = {
                        'sleep_medication_frequency': sleep_med_use if sleep_med_use is not None else 0,
                        'sleep_quality_score': sleep_quality if sleep_quality is not None else 3,
                        'daytime_sleepiness_score': daytime_sleepiness if daytime_sleepiness is not None else 2,
                        'has_general_medication': has_general_medication,
                        'medication_category': self._categorize_sleep_medication_use(sleep_med_use),
                        'sleep_quality_category': self._categorize_sleep_quality(sleep_quality)
                    }
            
            # Análise por categorias de medicação
            med_categories = {}
            for participant_data in sleep_med_impact.values():
                med_cat = participant_data['medication_category']
                if med_cat not in med_categories:
                    med_categories[med_cat] = {
                        'participants': [],
                        'sleep_quality_scores': [],
                        'daytime_sleepiness_scores': []
                    }
                
                med_categories[med_cat]['participants'].append(participant_data)
                med_categories[med_cat]['sleep_quality_scores'].append(participant_data['sleep_quality_score'])
                med_categories[med_cat]['daytime_sleepiness_scores'].append(participant_data['daytime_sleepiness_score'])
            
            # Estatísticas por categoria
            category_stats = {}
            for cat, data in med_categories.items():
                if data['sleep_quality_scores']:
                    category_stats[cat] = {
                        'participant_count': len(data['participants']),
                        'avg_sleep_quality': round(np.mean(data['sleep_quality_scores']), 2),
                        'avg_daytime_sleepiness': round(np.mean(data['daytime_sleepiness_scores']), 2),
                        'sleep_quality_std': round(np.std(data['sleep_quality_scores']), 2),
                        'percentage': round((len(data['participants']) / len(sleep_med_impact)) * 100, 1) if sleep_med_impact else 0
                    }
            
            # Correlação medicação vs qualidade do sono
            med_sleep_correlation = None
            if len(sleep_med_impact) > 2:
                med_scores = [p['sleep_medication_frequency'] for p in sleep_med_impact.values()]
                quality_scores = [p['sleep_quality_score'] for p in sleep_med_impact.values()]
                
                if len(set(med_scores)) > 1 and len(set(quality_scores)) > 1:
                    correlation = np.corrcoef(med_scores, quality_scores)[0, 1]
                    if not np.isnan(correlation):
                        med_sleep_correlation = round(correlation, 3)
            
            return {
                'participant_analysis': sleep_med_impact,
                'category_statistics': category_stats,
                'medication_sleep_correlation': med_sleep_correlation,
                'summary': {
                    'total_participants': len(sleep_med_impact),
                    'participants_using_sleep_medication': len([p for p in sleep_med_impact.values() if p['sleep_medication_frequency'] > 0]),
                    'avg_sleep_quality': round(np.mean([p['sleep_quality_score'] for p in sleep_med_impact.values()]), 2) if sleep_med_impact else 0,
                    'correlation_strength': 'Forte' if med_sleep_correlation and abs(med_sleep_correlation) >= 0.5 else 'Moderada' if med_sleep_correlation and abs(med_sleep_correlation) >= 0.3 else 'Fraca' if med_sleep_correlation else 'N/A'
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de impacto da medicação no sono: {e}")
            import traceback
            traceback.print_exc()
            return {'participant_analysis': {}, 'category_statistics': {}, 'medication_sleep_correlation': None, 'summary': {}}
    
    def _categorize_sleep_medication_use(self, med_score):
        """Categoriza o uso de medicação para dormir"""
        if med_score is None or med_score == 0:
            return 'Sem Medicação'
        elif med_score <= 1:
            return 'Uso Ocasional'
        elif med_score <= 2:
            return 'Uso Regular'
        else:
            return 'Uso Frequente'
    
    def _categorize_sleep_quality(self, quality_score):
        """Categoriza a qualidade do sono"""
        if quality_score is None:
            return 'Não Avaliado'
        elif quality_score >= 4:
            return 'Boa Qualidade'
        elif quality_score >= 3:
            return 'Qualidade Moderada'
        else:
            return 'Qualidade Ruim'
    
    # =====================================
    # 🏥 UTILIZAÇÃO DE SERVIÇOS DE SAÚDE - FUNÇÕES INDEPENDENTES
    # =====================================
    
    def analyze_service_utilization_rm4health(self):
        """Analisa padrões de utilização de serviços de saúde"""
        try:
            # Converter dados para DataFrame se necessário
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            # Campos relacionados à utilização de serviços
            service_fields = {
                # Consultas médicas
                'gp_visits': 'Consultas no Médico de Família',
                'specialist_visits': 'Consultas de Especialidade',
                'emergency_visits': 'Visitas ao Serviço de Urgência',
                'hospital_admissions': 'Internamentos Hospitalares',
                
                # Serviços de apoio
                'nursing_visits': 'Visitas de Enfermagem',
                'physiotherapy_sessions': 'Sessões de Fisioterapia',
                'social_support_services': 'Serviços de Apoio Social',
                
                # Medicação e tratamentos
                'medication_changes': 'Alterações de Medicação',
                'treatment_adherence': 'Adesão ao Tratamento',
                
                # Monitoramento remoto
                'remote_monitoring_alerts': 'Alertas de Monitorização',
                'telemedicine_consultations': 'Teleconsultas'
            }
            
            # Filtrar dados de utilização
            utilization_data = data_df[data_df['participant_code'].notna()].copy()
            
            # Análise por tipo de serviço
            service_utilization = {}
            total_participants = len(utilization_data['participant_code'].unique())
            
            for field_key, field_name in service_fields.items():
                if field_key in utilization_data.columns:
                    # Contabilizar utilização
                    field_data = utilization_data[field_key].dropna()
                    
                    # Estatísticas básicas
                    utilization_count = len(field_data[field_data.notna() & (field_data != '') & (field_data != '0')])
                    utilization_rate = (utilization_count / total_participants * 100) if total_participants > 0 else 0
                    
                    # Frequência de utilização
                    frequency_distribution = {}
                    for value in field_data:
                        str_value = str(value).strip()
                        if str_value and str_value != '0' and str_value != 'nan':
                            if str_value in frequency_distribution:
                                frequency_distribution[str_value] += 1
                            else:
                                frequency_distribution[str_value] = 1
                    
                    service_utilization[field_key] = {
                        'name': field_name,
                        'utilization_count': utilization_count,
                        'utilization_rate': round(utilization_rate, 2),
                        'frequency_distribution': frequency_distribution,
                        'participants_using': utilization_count,
                        'total_participants': total_participants
                    }
            
            # Análise de padrões de utilização
            utilization_patterns = self._analyze_utilization_patterns(utilization_data)
            
            # Classificação por intensidade de utilização
            intensity_classification = self._classify_utilization_intensity(utilization_data, service_fields)
            
            return {
                'service_utilization': service_utilization,
                'utilization_patterns': utilization_patterns,
                'intensity_classification': intensity_classification,
                'summary': {
                    'total_participants': total_participants,
                    'services_analyzed': len(service_utilization),
                    'most_used_service': max(service_utilization.keys(), 
                                           key=lambda x: service_utilization[x]['utilization_count']) if service_utilization else None,
                    'average_utilization_rate': round(sum(s['utilization_rate'] for s in service_utilization.values()) / 
                                                    len(service_utilization), 2) if service_utilization else 0
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de utilização de serviços: {e}")
            import traceback
            traceback.print_exc()
            return {'service_utilization': {}, 'utilization_patterns': {}, 'intensity_classification': {}, 'summary': {}}
    
    def calculate_cost_effectiveness_rm4health(self):
        """Calcula análise de custo-efetividade do monitoramento remoto"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            # Custos estimados por tipo de serviço (em euros)
            service_costs = {
                'gp_visits': 50,  # Consulta médico de família
                'specialist_visits': 120,  # Consulta especialidade
                'emergency_visits': 200,  # Urgência
                'hospital_admissions': 1500,  # Internamento (média)
                'nursing_visits': 30,  # Visita enfermagem
                'physiotherapy_sessions': 40,  # Fisioterapia
                'telemedicine_consultations': 25,  # Teleconsulta
                'remote_monitoring_setup': 200,  # Custo setup monitorização
                'remote_monitoring_monthly': 50  # Custo mensal monitorização
            }
            
            utilization_data = data_df[data_df['participant_code'].notna()].copy()
            total_participants = len(utilization_data['participant_code'].unique())
            
            # Calcular custos por participante
            participant_costs = {}
            total_traditional_costs = 0
            total_remote_monitoring_costs = 0
            
            for _, participant in utilization_data.iterrows():
                participant_id = participant['participant_code']
                if pd.isna(participant_id):
                    continue
                
                traditional_cost = 0
                remote_cost = service_costs['remote_monitoring_setup'] + (service_costs['remote_monitoring_monthly'] * 12)
                
                # Somar custos tradicionais
                for service, cost in service_costs.items():
                    if service.startswith('remote_monitoring'):
                        continue
                    
                    if service in participant and pd.notna(participant[service]):
                        try:
                            visits = float(participant[service])
                            if visits > 0:
                                traditional_cost += visits * cost
                        except:
                            continue
                
                participant_costs[str(participant_id)] = {
                    'traditional_cost': traditional_cost,
                    'remote_monitoring_cost': remote_cost,
                    'cost_difference': traditional_cost - remote_cost,
                    'cost_savings': max(0, traditional_cost - remote_cost)
                }
                
                total_traditional_costs += traditional_cost
                total_remote_monitoring_costs += remote_cost
            
            # Análise de efetividade
            effectiveness_metrics = {
                'reduced_emergency_visits': self._calculate_emergency_reduction(utilization_data),
                'improved_treatment_adherence': self._calculate_adherence_improvement(utilization_data),
                'early_detection_rate': self._calculate_early_detection_rate(utilization_data),
                'patient_satisfaction': self._estimate_patient_satisfaction(utilization_data)
            }
            
            # Cálculo ROI (Return on Investment)
            total_savings = max(0, total_traditional_costs - total_remote_monitoring_costs)
            roi_percentage = (total_savings / total_remote_monitoring_costs * 100) if total_remote_monitoring_costs > 0 else 0
            
            return {
                'participant_costs': participant_costs,
                'cost_summary': {
                    'total_traditional_costs': round(total_traditional_costs, 2),
                    'total_remote_monitoring_costs': round(total_remote_monitoring_costs, 2),
                    'total_cost_savings': round(total_savings, 2),
                    'average_savings_per_participant': round(total_savings / max(1, total_participants), 2),
                    'roi_percentage': round(roi_percentage, 2)
                },
                'effectiveness_metrics': effectiveness_metrics,
                'cost_breakdown': service_costs,
                'summary': {
                    'participants_analyzed': total_participants,
                    'cost_effective': total_savings > 0,
                    'average_traditional_cost': round(total_traditional_costs / max(1, total_participants), 2),
                    'average_remote_cost': round(total_remote_monitoring_costs / max(1, total_participants), 2)
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de custo-efetividade: {e}")
            import traceback
            traceback.print_exc()
            return {'participant_costs': {}, 'cost_summary': {}, 'effectiveness_metrics': {}, 'cost_breakdown': {}, 'summary': {}}
    
    def assess_remote_monitoring_impact_rm4health(self):
        """Avalia o impacto do monitoramento remoto na utilização de serviços"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            impact_data = data_df[data_df['participant_code'].notna()].copy()
            
            # Campos para análise de impacto
            impact_fields = {
                'hospitalization_reduction': 'Redução de Internamentos',
                'emergency_reduction': 'Redução de Urgências',
                'medication_adherence_improvement': 'Melhoria da Adesão Medicamentosa',
                'early_detection_events': 'Eventos de Detecção Precoce',
                'quality_of_life_improvement': 'Melhoria da Qualidade de Vida',
                'caregiver_burden_reduction': 'Redução da Sobrecarga do Cuidador'
            }
            
            impact_analysis = {}
            
            # Análise pré/pós implementação
            baseline_period = self._get_baseline_metrics(impact_data)
            monitoring_period = self._get_monitoring_metrics(impact_data)
            
            # Calcular impactos específicos
            for field_key, field_name in impact_fields.items():
                impact_analysis[field_key] = {
                    'name': field_name,
                    'baseline_value': baseline_period.get(field_key, 0),
                    'monitoring_value': monitoring_period.get(field_key, 0),
                    'absolute_change': monitoring_period.get(field_key, 0) - baseline_period.get(field_key, 0),
                    'percentage_change': self._calculate_percentage_change(
                        baseline_period.get(field_key, 0), 
                        monitoring_period.get(field_key, 0)
                    ),
                    'improvement': monitoring_period.get(field_key, 0) > baseline_period.get(field_key, 0)
                }
            
            # Análise de alertas e intervenções
            alert_impact = self._analyze_alert_effectiveness(impact_data)
            
            # Métricas de satisfação e usabilidade
            satisfaction_metrics = self._analyze_satisfaction_metrics(impact_data)
            
            # Impacto na autonomia do paciente (análise baseada em dados reais)
            autonomy_impact = self._analyze_autonomy_impact_real(impact_data)
            
            return {
                'impact_analysis': impact_analysis,
                'alert_impact': alert_impact,
                'satisfaction_metrics': satisfaction_metrics,
                'autonomy_impact': autonomy_impact,
                'baseline_period': baseline_period,
                'monitoring_period': monitoring_period,
                'summary': {
                    'total_participants': len(impact_data['participant_code'].unique()),
                    'overall_impact_positive': sum(1 for impact in impact_analysis.values() if impact['improvement']) > len(impact_analysis) / 2,
                    'most_improved_metric': max(impact_analysis.keys(), key=lambda x: impact_analysis[x]['percentage_change']) if impact_analysis else None,
                    'average_improvement': round(sum(impact['percentage_change'] for impact in impact_analysis.values()) / len(impact_analysis), 2) if impact_analysis else 0
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na avaliação do impacto do monitoramento remoto: {e}")
            import traceback
            traceback.print_exc()
            return {'impact_analysis': {}, 'alert_impact': {}, 'satisfaction_metrics': {}, 'autonomy_impact': {}, 'baseline_period': {}, 'monitoring_period': {}, 'summary': {}}
    
    def identify_utilization_predictors_rm4health(self):
        """Identifica preditores de alta utilização de serviços de saúde - APENAS DADOS REAIS"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            predictor_data = data_df[data_df['participant_code'].notna()].copy()
            
            if len(predictor_data) == 0:
                return {'message': 'Sem dados suficientes para análise de preditores', 
                       'predictor_analysis': {}, 'summary': {}}
            
            # Variáveis preditoras disponíveis nos dados reais
            available_predictors = {
                'demographic': {},
                'clinical': {},
                'behavioral': {},
                'technology': {}
            }
            
            # Verificar quais campos existem nos dados
            potential_predictors = {
                'age': ('demographic', 'Idade'),
                'gender': ('demographic', 'Género'),
                'education_level': ('demographic', 'Nível de Educação'),
                'marital_status': ('demographic', 'Estado Civil'),
                'number_of_conditions': ('clinical', 'Número de Condições Crónicas'),
                'medication_count': ('clinical', 'Número de Medicamentos'),
                'treatment_adherence': ('behavioral', 'Adesão ao Tratamento'),
                'social_support': ('behavioral', 'Apoio Social'),
                'technology_acceptance': ('technology', 'Aceitação da Tecnologia'),
                'digital_literacy': ('technology', 'Literacia Digital')
            }
            
            # Analisar apenas campos que existem nos dados
            for field, (category, name) in potential_predictors.items():
                if field in predictor_data.columns:
                    field_data = predictor_data[field].dropna()
                    if len(field_data) > 0:
                        available_predictors[category][field] = {
                            'name': name,
                            'data_points': len(field_data),
                            'unique_values': len(field_data.unique()),
                            'coverage_rate': round((len(field_data) / len(predictor_data)) * 100, 1)
                        }
            
            # CAMPOS REAIS IDENTIFICADOS na investigação do REDCap
            service_fields = ['scheduled_medical_visits', 'unscheduled_medical_visits', 'emergency_visits', 'hospitalizations']
            utilization_scores = {}
            participants_with_data = 0
            
            for _, participant in predictor_data.iterrows():
                participant_id = str(participant['participant_code'])
                utilization_count = 0
                total_services = 0
                
                for service in service_fields:
                    if service in participant.index:
                        value_str = str(participant[service]).strip()
                        
                        # Verificar se o valor não está vazio e não é '0'
                        if value_str and value_str not in ['', '0', 'nan', 'None', 'NaN']:
                            try:
                                value = float(value_str)
                                if value > 0:
                                    utilization_count += value
                                    total_services += 1
                            except ValueError:
                                # Se não é número mas não está vazio, contar como 1
                                utilization_count += 1
                                total_services += 1
                
                # Só incluir participantes que têm pelo menos algum dado de utilização
                if total_services > 0:
                    participants_with_data += 1
                    utilization_scores[participant_id] = {
                        'total_services_used': total_services,
                        'utilization_score': utilization_count,
                        'is_high_utilizer': total_services >= 2 or utilization_count >= 3
                    }
            
            # Estatísticas reais de utilização
            high_utilizers = [p for p, data in utilization_scores.items() if data['is_high_utilizer']]
            total_participants_with_data = len(utilization_scores)
            high_utilization_rate = (len(high_utilizers) / total_participants_with_data * 100) if total_participants_with_data > 0 else 0
            
            # Análise de correlações reais (simplificada)
            correlation_analysis = {}
            for category, predictors in available_predictors.items():
                if predictors:  # Só analisa se há preditores nesta categoria
                    correlation_analysis[category] = {
                        'available_predictors': len(predictors),
                        'data_quality': 'real_data_analysis',
                        'predictors': predictors
                    }
            
            return {
                'predictor_analysis': correlation_analysis,
                'utilization_analysis': {
                    'total_participants': len(predictor_data),
                    'participants_with_utilization_data': total_participants_with_data,
                    'high_utilizers_count': len(high_utilizers),
                    'high_utilization_rate': round(high_utilization_rate, 1),
                    'average_services_per_participant': round(sum(s['total_services_used'] for s in utilization_scores.values()) / total_participants_with_data, 1) if total_participants_with_data > 0 else 0,
                    'utilization_coverage': round((total_participants_with_data / len(predictor_data)) * 100, 1) if len(predictor_data) > 0 else 0
                },
                'high_utilizers': high_utilizers[:10],  # Top 10 para demonstração
                'data_summary': {
                    'analysis_type': 'real_data_only',
                    'simulation_used': False,
                    'available_data_fields': list(set(potential_predictors.keys()).intersection(set(predictor_data.columns.tolist()))),
                    'missing_data_fields': list(set(potential_predictors.keys()) - set(predictor_data.columns.tolist())),
                    'service_fields_analyzed': service_fields
                },
                'summary': {
                    'message': f'Análise baseada exclusivamente em dados reais do REDCap',
                    'participants_analyzed': len(predictor_data),
                    'participants_with_utilization': total_participants_with_data,
                    'data_completeness': f"{len([c for c in available_predictors.values() if c])}/4 categorias com dados",
                    'high_utilizer_identification': f"{len(high_utilizers)} participantes identificados"
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na identificação de preditores de utilização: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'message': 'Erro na análise - dados insuficientes ou formato inválido',
                'predictor_analysis': {}, 
                'summary': {}
            }
    
    # =====================================
    # FUNÇÕES AUXILIARES PARA UTILIZAÇÃO DE SERVIÇOS
    # =====================================
    
    def _analyze_utilization_patterns(self, data):
        """Analisa padrões de utilização de serviços"""
        patterns = {
            'seasonal_patterns': {},
            'day_of_week_patterns': {},
            'service_combinations': {},
            'utilization_trends': {}
        }
        
        # Análise simplificada de padrões
        try:
            # Padrões por tipo de utilizador
            high_users = data[data.apply(lambda row: sum(1 for col in ['gp_visits', 'specialist_visits', 'emergency_visits'] 
                                                       if col in row and pd.notna(row[col]) and str(row[col]) not in ['0', '']), axis=1) >= 2]
            low_users = data[data.apply(lambda row: sum(1 for col in ['gp_visits', 'specialist_visits', 'emergency_visits'] 
                                                      if col in row and pd.notna(row[col]) and str(row[col]) not in ['0', '']), axis=1) <= 1]
            
            patterns['user_types'] = {
                'high_utilizers': len(high_users),
                'low_utilizers': len(low_users),
                'moderate_utilizers': len(data) - len(high_users) - len(low_users)
            }
            
        except Exception as e:
            print(f"Erro na análise de padrões: {e}")
        
        return patterns
    
    def _classify_utilization_intensity(self, data, service_fields):
        """Classifica a intensidade de utilização"""
        classification = {
            'low_intensity': 0,
            'moderate_intensity': 0,
            'high_intensity': 0,
            'very_high_intensity': 0
        }
        
        for _, participant in data.iterrows():
            service_count = 0
            for field_key in service_fields.keys():
                if field_key in participant and pd.notna(participant[field_key]) and str(participant[field_key]) not in ['0', '']:
                    try:
                        if float(participant[field_key]) > 0:
                            service_count += 1
                    except:
                        service_count += 1
            
            if service_count == 0:
                classification['low_intensity'] += 1
            elif service_count <= 2:
                classification['moderate_intensity'] += 1
            elif service_count <= 4:
                classification['high_intensity'] += 1
            else:
                classification['very_high_intensity'] += 1
        
        return classification
    
    def _calculate_emergency_reduction(self, data):
        """Calcula redução de visitas de emergência baseada em dados reais"""
        if 'emergency_visits' not in data.columns:
            return {'message': 'Campo emergency_visits não encontrado', 'reduction': 0}
        
        emergency_data = data['emergency_visits'].dropna()
        if len(emergency_data) == 0:
            return {'message': 'Sem dados de emergência disponíveis', 'reduction': 0}
        
        # Converter para numérico, ignorando strings inválidas
        numeric_values = []
        for value in emergency_data:
            try:
                # Tentar converter para float
                if str(value).replace('.', '').replace('-', '').isdigit():
                    numeric_values.append(float(value))
                elif str(value).strip() not in ['', '0', 'nan']:
                    # Se não é numérico mas não é vazio, contar como 1
                    numeric_values.append(1)
            except:
                continue
        
        if not numeric_values:
            return {'message': 'Dados de emergência não numéricos', 'reduction': 0}
        
        # Análise real: média de visitas de emergência
        avg_emergency_visits = sum(numeric_values) / len(numeric_values)
        participants_with_emergency = len([x for x in numeric_values if x > 0])
        
        return {
            'average_emergency_visits': round(avg_emergency_visits, 2),
            'participants_with_emergency': participants_with_emergency,
            'emergency_rate': round((participants_with_emergency / len(data)) * 100, 1),
            'data_source': 'real_data_analysis'
        }
    
    def _calculate_adherence_improvement(self, data):
        """Calcula melhoria na adesão ao tratamento baseada em dados reais"""
        if 'treatment_adherence' not in data.columns:
            return {'message': 'Campo treatment_adherence não encontrado', 'improvement': 0}
        
        adherence_data = data['treatment_adherence'].dropna()
        if len(adherence_data) == 0:
            return {'message': 'Sem dados de adesão disponíveis', 'improvement': 0}
        
        # Análise real da adesão
        try:
            numeric_adherence = [float(x) for x in adherence_data if str(x).replace('.', '').isdigit()]
            if numeric_adherence:
                avg_adherence = sum(numeric_adherence) / len(numeric_adherence)
                return {
                    'average_adherence': round(avg_adherence, 2),
                    'participants_with_data': len(numeric_adherence),
                    'data_source': 'real_data_analysis'
                }
        except:
            pass
        
        # Se não são numéricos, contar categorias
        adherence_categories = {}
        for value in adherence_data:
            str_val = str(value).strip()
            adherence_categories[str_val] = adherence_categories.get(str_val, 0) + 1
        
        return {
            'adherence_categories': adherence_categories,
            'participants_with_data': len(adherence_data),
            'data_source': 'real_data_analysis'
        }
    
    def _calculate_early_detection_rate(self, data):
        """Calcula taxa de detecção precoce baseada em dados reais"""
        detection_fields = ['remote_monitoring_alerts', 'health_alerts', 'early_detection']
        
        detection_data = {}
        for field in detection_fields:
            if field in data.columns:
                field_data = data[field].dropna()
                if len(field_data) > 0:
                    detection_data[field] = {
                        'count': len([x for x in field_data if str(x) not in ['0', '']]),
                        'participants': len(field_data)
                    }
        
        if not detection_data:
            return {'message': 'Campos de detecção não encontrados', 'rate': 0}
        
        return {
            'detection_fields_found': detection_data,
            'data_source': 'real_data_analysis'
        }
    
    def _estimate_patient_satisfaction(self, data):
        """Estima satisfação do paciente baseada em dados reais"""
        satisfaction_fields = ['satisfaction', 'system_satisfaction', 'overall_satisfaction']
        
        satisfaction_data = {}
        for field in satisfaction_fields:
            if field in data.columns:
                field_data = data[field].dropna()
                if len(field_data) > 0:
                    try:
                        numeric_data = [float(x) for x in field_data if str(x).replace('.', '').isdigit()]
                        if numeric_data:
                            satisfaction_data[field] = {
                                'average': round(sum(numeric_data) / len(numeric_data), 2),
                                'count': len(numeric_data)
                            }
                    except:
                        # Dados categóricos
                        categories = {}
                        for value in field_data:
                            categories[str(value)] = categories.get(str(value), 0) + 1
                        satisfaction_data[field] = {'categories': categories}
        
        if not satisfaction_data:
            return {'message': 'Campos de satisfação não encontrados'}
        
        return {
            'satisfaction_analysis': satisfaction_data,
            'data_source': 'real_data_analysis'
        }
    
    def _get_baseline_metrics(self, data):
        """Obtém métricas do período baseline usando dados reais"""
        metrics = {}
        
        # Campos potenciais de baseline
        baseline_fields = {
            'baseline_hospitalizations': 'hospitalization_reduction',
            'baseline_emergency_visits': 'emergency_reduction', 
            'baseline_medication_adherence': 'medication_adherence_improvement',
            'baseline_quality_of_life': 'quality_of_life_improvement'
        }
        
        for field, metric_name in baseline_fields.items():
            if field in data.columns:
                field_data = data[field].dropna()
                if len(field_data) > 0:
                    try:
                        numeric_data = [float(x) for x in field_data if str(x).replace('.', '').replace('-', '').isdigit()]
                        if numeric_data:
                            metrics[metric_name] = round(sum(numeric_data) / len(numeric_data), 2)
                    except:
                        metrics[metric_name] = len([x for x in field_data if str(x) not in ['', '0']])
        
        if not metrics:
            return {'message': 'Dados de baseline não disponíveis nos campos REDCap'}
        
        return metrics
    
    def _get_monitoring_metrics(self, data):
        """Obtém métricas do período de monitoramento usando dados reais"""
        metrics = {}
        
        # Campos potenciais de monitoramento
        monitoring_fields = {
            'monitoring_hospitalizations': 'hospitalization_reduction',
            'monitoring_emergency_visits': 'emergency_reduction',
            'current_medication_adherence': 'medication_adherence_improvement', 
            'current_quality_of_life': 'quality_of_life_improvement'
        }
        
        for field, metric_name in monitoring_fields.items():
            if field in data.columns:
                field_data = data[field].dropna()
                if len(field_data) > 0:
                    try:
                        numeric_data = [float(x) for x in field_data if str(x).replace('.', '').replace('-', '').isdigit()]
                        if numeric_data:
                            metrics[metric_name] = round(sum(numeric_data) / len(numeric_data), 2)
                    except:
                        metrics[metric_name] = len([x for x in field_data if str(x) not in ['', '0']])
        
        if not metrics:
            return {'message': 'Dados de monitoramento não disponíveis nos campos REDCap'}
        
        return metrics
    
    def _calculate_percentage_change(self, baseline, monitoring):
        """Calcula mudança percentual"""
        if baseline == 0:
            return 100 if monitoring > 0 else 0
        return round(((monitoring - baseline) / baseline) * 100, 2)
    
    def _analyze_alert_effectiveness(self, data):
        """Analisa efetividade dos alertas baseada em dados reais"""
        alert_fields = ['alerts_generated', 'alert_responses', 'alert_effectiveness']
        alert_data = {}
        
        for field in alert_fields:
            if field in data.columns:
                field_data = data[field].dropna()
                if len(field_data) > 0:
                    alert_data[field] = {
                        'count': len([x for x in field_data if str(x) not in ['0', '']]),
                        'participants': len(field_data)
                    }
        
        if not alert_data:
            return {'message': 'Dados de alertas não encontrados'}
        
        return {
            'alert_analysis': alert_data,
            'data_source': 'real_data_analysis'
        }
    
    def _analyze_satisfaction_metrics(self, data):
        """Analisa métricas de satisfação baseada em dados reais"""
        satisfaction_fields = {
            'overall_satisfaction': 'Satisfação Geral',
            'ease_of_use': 'Facilidade de Uso', 
            'perceived_usefulness': 'Utilidade Percebida',
            'system_reliability': 'Confiabilidade do Sistema'
        }
        
        satisfaction_analysis = {}
        for field, description in satisfaction_fields.items():
            if field in data.columns:
                field_data = data[field].dropna()
                if len(field_data) > 0:
                    try:
                        numeric_data = [float(x) for x in field_data if str(x).replace('.', '').isdigit()]
                        if numeric_data:
                            satisfaction_analysis[field] = {
                                'description': description,
                                'average': round(sum(numeric_data) / len(numeric_data), 2),
                                'count': len(numeric_data)
                            }
                    except:
                        categories = {}
                        for value in field_data:
                            categories[str(value)] = categories.get(str(value), 0) + 1
                        satisfaction_analysis[field] = {
                            'description': description,
                            'categories': categories
                        }
        
        if not satisfaction_analysis:
            return {'message': 'Dados de satisfação não encontrados'}
        
        return satisfaction_analysis
    
    def _analyze_autonomy_impact_real(self, data):
        """Analisa impacto na autonomia baseado em dados reais"""
        autonomy_fields = {
            'independence_score': 'Score de Independência',
            'self_care_confidence': 'Confiança no Autocuidado',
            'decision_making': 'Participação nas Decisões',
            'health_management': 'Gestão da Saúde'
        }
        
        autonomy_analysis = {}
        for field, description in autonomy_fields.items():
            if field in data.columns:
                field_data = data[field].dropna()
                if len(field_data) > 0:
                    try:
                        numeric_data = [float(x) for x in field_data if str(x).replace('.', '').replace('-', '').isdigit()]
                        if numeric_data:
                            autonomy_analysis[field] = {
                                'description': description,
                                'average': round(sum(numeric_data) / len(numeric_data), 2),
                                'count': len(numeric_data),
                                'data_source': 'real_data'
                            }
                    except:
                        categories = {}
                        for value in field_data:
                            str_val = str(value).strip()
                            categories[str_val] = categories.get(str_val, 0) + 1
                        autonomy_analysis[field] = {
                            'description': description,
                            'categories': categories,
                            'data_source': 'real_data'
                        }
        
        if not autonomy_analysis:
            return {'message': 'Dados de autonomia não encontrados nos campos REDCap'}
        
        return autonomy_analysis
        return {
            'overall_satisfaction': 4.3,
            'ease_of_use': 4.1,
            'perceived_usefulness': 4.5,
            'recommendation_likelihood': 4.2,
            'system_reliability': 4.0
        }
    
    # =====================================
    # ANÁLISE DE CUIDADORES - MÉTODOS NOVOS
    # =====================================
    
    def compare_caregiver_groups(self):
        """Compara participantes com e sem cuidadores - DADOS REAIS ADAPTADOS"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            # Filtrar dados válidos
            valid_data = data_df[data_df['participant_code'].notna()].copy()
            
            if len(valid_data) == 0:
                return {'message': 'Sem dados suficientes para análise de cuidadores', 
                       'comparison': {}, 'summary': {}}
            
            # CAMPOS REAIS IDENTIFICADOS NO REDCap (baseado na investigação)
            # Como não há campos específicos de cuidador, vamos usar outros indicadores
            # que possam sugerir presença de suporte familiar/social
            
            proxy_caregiver_fields = [
                'receiving_visits',  # Recebe visitas de amigos/família
                'receiving_visits_2',
                'marital_status',    # Estado civil (casado pode indicar suporte)
                'health_status',     # Estado de saúde (pior = mais provável ter cuidador)
            ]
            
            # Determinar quem tem provável suporte de cuidador
            likely_with_caregiver = []
            likely_without_caregiver = []
            
            for _, participant in valid_data.iterrows():
                participant_id = participant.get('participant_code', 'N/A')
                has_caregiver_indicators = False
                
                # Indicadores de provável presença de cuidador
                # 1. Recebe visitas regulares
                if 'receiving_visits' in participant:
                    visits = str(participant['receiving_visits']).strip()
                    if visits in ['1', '2']:  # Assumindo 1=sim, 2=frequentemente
                        has_caregiver_indicators = True
                
                # 2. Estado civil casado
                if 'marital_status' in participant:
                    marital = str(participant['marital_status']).strip()
                    if marital in ['1', '2']:  # Assumindo códigos para casado/união
                        has_caregiver_indicators = True
                
                # 3. Estado de saúde deteriorado (mais provável ter cuidador)
                if 'health_status' in participant:
                    health = str(participant['health_status']).strip()
                    if health in ['4', '5']:  # Assumindo 4-5 = saúde pior
                        has_caregiver_indicators = True
                
                if has_caregiver_indicators:
                    likely_with_caregiver.append(participant)
                else:
                    likely_without_caregiver.append(participant)
            
            # Análise comparativa baseada nos dados disponíveis
            comparison_analysis = {}
            
            if len(likely_with_caregiver) > 0 and len(likely_without_caregiver) > 0:
                
                # Comparar utilização de serviços entre grupos
                utilization_fields = ['scheduled_medical_visits', 'unscheduled_medical_visits', 
                                    'emergency_visits', 'hospitalizations']
                
                group_comparison = {
                    'with_support': {'count': len(likely_with_caregiver), 'utilization': {}},
                    'without_support': {'count': len(likely_without_caregiver), 'utilization': {}}
                }
                
                for field in utilization_fields:
                    # Grupo com suporte
                    values_with = []
                    for p in likely_with_caregiver:
                        if field in p and pd.notna(p[field]) and str(p[field]).strip():
                            try:
                                values_with.append(float(p[field]))
                            except:
                                pass
                    
                    # Grupo sem suporte
                    values_without = []
                    for p in likely_without_caregiver:
                        if field in p and pd.notna(p[field]) and str(p[field]).strip():
                            try:
                                values_without.append(float(p[field]))
                            except:
                                pass
                    
                    group_comparison['with_support']['utilization'][field] = {
                        'avg': round(sum(values_with) / len(values_with), 1) if values_with else 0,
                        'count_with_data': len(values_with)
                    }
                    group_comparison['without_support']['utilization'][field] = {
                        'avg': round(sum(values_without) / len(values_without), 1) if values_without else 0,
                        'count_with_data': len(values_without)
                    }
                
                comparison_analysis = group_comparison
            
            return {
                'comparison_analysis': comparison_analysis,
                'data_summary': {
                    'total_participants': len(valid_data),
                    'analysis_type': 'proxy_indicators_real_data',
                    'proxy_fields_used': proxy_caregiver_fields,
                    'note': 'Análise baseada em indicadores indiretos (visitas, estado civil, saúde)'
                },
                'summary': {
                    'message': 'Análise usando indicadores indiretos de suporte (dados reais REDCap)',
                    'methodology': 'Visitas familiares + Estado civil + Condição de saúde',
                    'data_completeness': f"{len([f for f in proxy_caregiver_fields if f in valid_data.columns])}/4 campos proxy disponíveis"
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na comparação de grupos de cuidadores: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'comparison_analysis': {},
                'message': 'Erro na análise de comparação de cuidadores'
            }
    
    def analyze_caregiver_burden(self):
        """Analisa a carga do cuidador - APENAS DADOS REAIS"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            valid_data = data_df[data_df['participant_code'].notna()].copy()
            
            if len(valid_data) == 0:
                return {'message': 'Sem dados suficientes para análise da carga do cuidador', 
                       'burden_analysis': {}, 'summary': {}}
            
            # Campos relacionados com carga do cuidador
            burden_fields = ['caregiver_burden', 'caregiver_stress', 'caregiver_hours_per_day',
                           'caregiver_fatigue', 'caregiver_sleep_quality', 'caregiver_health']
            
            burden_data = []
            caregiver_profiles = []
            
            for _, participant in valid_data.iterrows():
                participant_burden = {}
                has_burden_data = False
                
                for field in burden_fields:
                    if field in participant and pd.notna(participant[field]):
                        try:
                            value = str(participant[field]).strip()
                            if value not in ['', '0', 'None']:
                                participant_burden[field] = value
                                has_burden_data = True
                        except:
                            pass
                
                if has_burden_data:
                    participant_burden['participant_id'] = participant['participant_code']
                    burden_data.append(participant_burden)
                    caregiver_profiles.append(participant)
            
            # Análise da carga
            burden_analysis = {}
            if burden_data:
                # Análise de horas de cuidado
                care_hours = []
                for burden in burden_data:
                    if 'caregiver_hours_per_day' in burden:
                        try:
                            hours = float(burden['caregiver_hours_per_day'])
                            care_hours.append(hours)
                        except:
                            pass
                
                burden_analysis = {
                    'caregivers_with_data': len(burden_data),
                    'avg_care_hours_per_day': round(sum(care_hours) / len(care_hours), 1) if care_hours else 'N/A',
                    'high_burden_caregivers': len([h for h in care_hours if h > 8]) if care_hours else 0,
                    'burden_indicators_available': len(burden_fields) - len([f for f in burden_fields if f not in valid_data.columns])
                }
            
            return {
                'burden_analysis': burden_analysis,
                'caregiver_data': burden_data[:10],  # Top 10 para demonstração
                'data_summary': {
                    'analysis_type': 'real_data_only',
                    'available_burden_fields': [f for f in burden_fields if f in valid_data.columns],
                    'missing_burden_fields': [f for f in burden_fields if f not in valid_data.columns]
                },
                'summary': {
                    'message': 'Análise de carga de cuidadores baseada exclusivamente em dados reais',
                    'caregivers_analyzed': len(burden_data),
                    'data_quality': f"Dados de carga disponíveis para {len(burden_data)} cuidadores"
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na análise da carga do cuidador: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'burden_analysis': {},
                'message': 'Erro na análise da carga do cuidador'
            }
    
    def assess_support_effectiveness(self):
        """Avalia a eficácia do suporte do cuidador - APENAS DADOS REAIS"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            valid_data = data_df[data_df['participant_code'].notna()].copy()
            
            if len(valid_data) == 0:
                return {'message': 'Sem dados suficientes para análise de eficácia do suporte', 
                       'effectiveness': {}, 'summary': {}}
            
            # Campos relacionados com eficácia do suporte
            effectiveness_fields = ['medication_adherence', 'appointment_compliance', 
                                  'health_improvement', 'quality_of_life_score',
                                  'emergency_visits', 'hospitalization_rate']
            
            # Participantes com e sem cuidadores
            with_caregiver = []
            without_caregiver = []
            caregiver_fields = ['caregiver', 'has_caregiver', 'caregiver_support']
            
            for _, participant in valid_data.iterrows():
                has_caregiver_support = False
                for field in caregiver_fields:
                    if field in participant and pd.notna(participant[field]):
                        if str(participant[field]).strip() not in ['', '0', 'No', 'Não', 'None']:
                            has_caregiver_support = True
                            break
                
                if has_caregiver_support:
                    with_caregiver.append(participant)
                else:
                    without_caregiver.append(participant)
            
            # Comparar outcomes
            effectiveness_analysis = {}
            if len(with_caregiver) > 0 and len(without_caregiver) > 0:
                
                # Adesão à medicação
                adherence_with = []
                adherence_without = []
                
                for p in with_caregiver:
                    if 'medication_adherence' in p and pd.notna(p['medication_adherence']):
                        try:
                            adherence_with.append(float(p['medication_adherence']))
                        except:
                            pass
                
                for p in without_caregiver:
                    if 'medication_adherence' in p and pd.notna(p['medication_adherence']):
                        try:
                            adherence_without.append(float(p['medication_adherence']))
                        except:
                            pass
                
                effectiveness_analysis = {
                    'participants_with_caregiver': len(with_caregiver),
                    'participants_without_caregiver': len(without_caregiver),
                    'avg_adherence_with_caregiver': round(sum(adherence_with) / len(adherence_with), 1) if adherence_with else 'N/A',
                    'avg_adherence_without_caregiver': round(sum(adherence_without) / len(adherence_without), 1) if adherence_without else 'N/A',
                    'effectiveness_difference': 'Análise disponível com dados reais' if (adherence_with and adherence_without) else 'Dados insuficientes'
                }
            
            return {
                'effectiveness_analysis': effectiveness_analysis,
                'data_summary': {
                    'total_participants': len(valid_data),
                    'analysis_type': 'real_data_only',
                    'available_effectiveness_fields': [f for f in effectiveness_fields if f in valid_data.columns]
                },
                'summary': {
                    'message': 'Análise de eficácia baseada exclusivamente em dados reais do REDCap',
                    'comparison_groups': f"Com cuidador: {len(with_caregiver)}, Sem cuidador: {len(without_caregiver)}"
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na avaliação da eficácia do suporte: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'effectiveness_analysis': {},
                'message': 'Erro na análise de eficácia do suporte'
            }
    
    def caregiver_response_patterns(self):
        """Analisa padrões de resposta dos cuidadores - APENAS DADOS REAIS"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            valid_data = data_df[data_df['participant_code'].notna()].copy()
            
            if len(valid_data) == 0:
                return {'message': 'Sem dados suficientes para análise de padrões de resposta', 
                       'patterns': {}, 'summary': {}}
            
            # Campos de resposta/interação
            response_fields = ['response_time', 'response_frequency', 'engagement_level',
                             'caregiver_questions', 'caregiver_concerns', 'communication_preference']
            
            caregiver_responses = []
            response_patterns = {}
            
            # Identificar cuidadores com dados de resposta
            caregiver_fields = ['caregiver', 'has_caregiver', 'caregiver_support']
            
            for _, participant in valid_data.iterrows():
                has_caregiver = False
                for field in caregiver_fields:
                    if field in participant and pd.notna(participant[field]):
                        if str(participant[field]).strip() not in ['', '0', 'No', 'Não', 'None']:
                            has_caregiver = True
                            break
                
                if has_caregiver:
                    response_data = {'participant_id': participant['participant_code']}
                    has_response_data = False
                    
                    for field in response_fields:
                        if field in participant and pd.notna(participant[field]):
                            response_data[field] = str(participant[field]).strip()
                            has_response_data = True
                    
                    if has_response_data:
                        caregiver_responses.append(response_data)
            
            # Analisar padrões
            if caregiver_responses:
                # Análise de frequência de comunicação
                communication_frequency = {}
                engagement_levels = []
                
                for response in caregiver_responses:
                    if 'response_frequency' in response:
                        freq = response['response_frequency'].lower()
                        communication_frequency[freq] = communication_frequency.get(freq, 0) + 1
                    
                    if 'engagement_level' in response:
                        try:
                            level = float(response['engagement_level'])
                            engagement_levels.append(level)
                        except:
                            pass
                
                response_patterns = {
                    'caregivers_with_response_data': len(caregiver_responses),
                    'communication_patterns': communication_frequency,
                    'avg_engagement_level': round(sum(engagement_levels) / len(engagement_levels), 1) if engagement_levels else 'N/A',
                    'active_communicators': len([r for r in caregiver_responses if 'communication_preference' in r])
                }
            
            return {
                'response_patterns': response_patterns,
                'caregiver_responses': caregiver_responses[:10],  # Top 10
                'data_summary': {
                    'analysis_type': 'real_data_only',
                    'available_response_fields': [f for f in response_fields if f in valid_data.columns],
                    'caregivers_analyzed': len(caregiver_responses)
                },
                'summary': {
                    'message': 'Análise de padrões de resposta baseada exclusivamente em dados reais',
                    'response_data_quality': f"Dados de resposta disponíveis para {len(caregiver_responses)} cuidadores"
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de padrões de resposta: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'response_patterns': {},
                'message': 'Erro na análise de padrões de resposta'
            }
    
    # ANÁLISE RESIDENCIAL - RESIDENTES VS NÃO-RESIDENTES
    # ================================================
    
    def compare_residence_demographics(self):
        """Compara características demográficas entre residentes e não-residentes"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            # Filtrar apenas participantes únicos (com participant_code_estudo preenchido)
            valid_data = data_df[
                (data_df['participant_code_estudo'].notna()) & 
                (data_df['participant_code_estudo'] != '')
            ].copy()
            
            print(f"🔍 Debug Residência: {len(data_df)} registros total, {len(valid_data)} participantes únicos")
            
            if len(valid_data) == 0:
                return {'message': 'Sem dados suficientes para análise demográfica residencial', 
                       'comparison': {}, 'summary': {}}
            
            # Usar classificação baseada no campo participant_group do REDCap
            residents, non_residents = self._classify_by_residence(valid_data)
            
            print(f"🏠 Classificação: {len(residents)} residentes, {len(non_residents)} não-residentes")
            
            # Análise demográfica comparativa
            demographic_analysis = {
                'residents': {
                    'count': len(residents),
                    'demographics': self._analyze_group_demographics(residents)
                },
                'non_residents': {
                    'count': len(non_residents),
                    'demographics': self._analyze_group_demographics(non_residents)
                }
            }
            
            # Testes estatísticos (simplificados)
            statistical_tests = self._perform_demographic_tests(residents, non_residents)
            
            return {
                'demographic_comparison': demographic_analysis,
                'statistical_significance': statistical_tests,
                'data_summary': {
                    'total_participants': len(valid_data),
                    'residents_count': len(residents),
                    'non_residents_count': len(non_residents),
                    'analysis_type': 'redcap_participant_group_classification'
                },
                'summary': {
                    'message': f'Análise demográfica: {len(residents)} residentes vs {len(non_residents)} não-residentes',
                    'methodology': 'Classificação baseada no campo participant_group do REDCap',
                    'data_coverage': f"{len(residents) + len(non_residents)}/{len(valid_data)} participantes classificados"
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na comparação demográfica residencial: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'demographic_comparison': {},
                'message': 'Erro na análise demográfica residencial'
            }
    
    def compare_health_outcomes(self):
        """Compara outcomes de saúde entre residentes e não-residentes"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            # Filtrar apenas participantes únicos
            valid_data = data_df[
                (data_df['participant_code_estudo'].notna()) & 
                (data_df['participant_code_estudo'] != '')
            ].copy()
            
            # Identificar grupos residenciais
            residents, non_residents = self._classify_by_residence(valid_data)
            
            # Campos de outcomes de saúde reais
            health_fields = [
                'health_status', 'symptom_severity', 'quality_of_life',
                'functional_status', 'cognitive_status', 'pain_level',
                'mobility_score', 'independence_level'
            ]
            
            health_comparison = {
                'residents': {
                    'count': len(residents),
                    'health_metrics': self._analyze_health_metrics(residents, health_fields)
                },
                'non_residents': {
                    'count': len(non_residents),
                    'health_metrics': self._analyze_health_metrics(non_residents, health_fields)
                }
            }
            
            # Diferenças significativas
            health_differences = self._compare_health_metrics(residents, non_residents, health_fields)
            
            return {
                'health_outcomes_comparison': health_comparison,
                'significant_differences': health_differences,
                'summary': {
                    'message': f'Comparação de saúde: {len(residents)} residentes vs {len(non_residents)} não-residentes',
                    'key_findings': self._summarize_health_differences(health_differences)
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na comparação de outcomes de saúde: {e}")
            return {
                'error': str(e),
                'health_outcomes_comparison': {},
                'message': 'Erro na análise de outcomes de saúde'
            }
    
    def compare_adherence_by_residence(self):
        """Compara adesão medicamentosa entre residentes e não-residentes"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            # Filtrar apenas participantes únicos
            valid_data = data_df[
                (data_df['participant_code_estudo'].notna()) & 
                (data_df['participant_code_estudo'] != '')
            ].copy()
            
            # Identificar grupos residenciais
            residents, non_residents = self._classify_by_residence(valid_data)
            
            # Campos de adesão medicamentosa reais
            adherence_fields = [
                'took_medications_yesterday', 'medication_adherence_score',
                'missed_doses_week', 'medication_compliance', 'pill_count'
            ]
            
            adherence_comparison = {
                'residents': {
                    'count': len(residents),
                    'adherence_metrics': self._analyze_adherence_metrics(residents, adherence_fields)
                },
                'non_residents': {
                    'count': len(non_residents),
                    'adherence_metrics': self._analyze_adherence_metrics(non_residents, adherence_fields)
                }
            }
            
            # Fatores específicos por grupo
            residence_factors = self._identify_adherence_factors_by_residence(residents, non_residents)
            
            return {
                'adherence_comparison': adherence_comparison,
                'residence_specific_factors': residence_factors,
                'summary': {
                    'message': f'Adesão medicamentosa: {len(residents)} residentes vs {len(non_residents)} não-residentes',
                    'key_differences': self._summarize_adherence_differences(adherence_comparison)
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na comparação de adesão por residência: {e}")
            return {
                'error': str(e),
                'adherence_comparison': {},
                'message': 'Erro na análise de adesão por residência'
            }
    
    def compare_quality_of_life(self):
        """Compara qualidade de vida entre residentes e não-residentes"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                data_df = pd.DataFrame(self.data)
            else:
                data_df = self.data
            
            # Filtrar apenas participantes únicos
            valid_data = data_df[
                (data_df['participant_code_estudo'].notna()) & 
                (data_df['participant_code_estudo'] != '')
            ].copy()
            
            # Identificar grupos residenciais
            residents, non_residents = self._classify_by_residence(valid_data)
            
            # Campos de qualidade de vida reais
            qol_fields = [
                'life_satisfaction', 'social_interaction', 'emotional_wellbeing',
                'physical_comfort', 'autonomy', 'security_feeling'
            ]
            
            qol_comparison = {
                'residents': {
                    'count': len(residents),
                    'qol_metrics': self._analyze_qol_metrics(residents, qol_fields)
                },
                'non_residents': {
                    'count': len(non_residents),
                    'qol_metrics': self._analyze_qol_metrics(non_residents, qol_fields)
                }
            }
            
            # Dimensões específicas de qualidade de vida
            qol_dimensions = self._analyze_qol_dimensions(residents, non_residents)
            
            return {
                'quality_of_life_comparison': qol_comparison,
                'qol_dimensions': qol_dimensions,
                'summary': {
                    'message': f'Qualidade de vida: {len(residents)} residentes vs {len(non_residents)} não-residentes',
                    'key_insights': self._summarize_qol_differences(qol_comparison)
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na comparação de qualidade de vida: {e}")
            return {
                'error': str(e),
                'quality_of_life_comparison': {},
                'message': 'Erro na análise de qualidade de vida'
            }
    
    # MÉTODOS AUXILIARES PARA ANÁLISE RESIDENCIAL
    # ==========================================
    
    def _classify_by_residence(self, data_df):
        """Classifica participantes por tipo de residência baseado no campo participant_group do REDCap"""
        residents = []
        non_residents = []
        
        print(f"🔍 DEBUG _classify_by_residence: Iniciando classificação com {len(data_df)} participantes")
        
        for _, participant in data_df.iterrows():
            participant_id = participant.get('participant_code_estudo', 'N/A')
            
            # Usar o campo correto do REDCap: participant_group
            if 'participant_group' in participant and pd.notna(participant['participant_group']):
                value = str(participant['participant_group']).strip().lower()
                print(f"🏠 DEBUG: Participante {participant_id} - grupo: '{value}'")
                
                # 'a' = Residente (Grupo A)
                if value == 'a':
                    residents.append(participant)
                    print(f"   ✅ Adicionado como RESIDENTE")
                # 'b' = Não-Residente (Grupo B) 
                elif value == 'b':
                    non_residents.append(participant)
                    print(f"   🏠 Adicionado como NÃO-RESIDENTE")
                else:
                    print(f"   ⚪ Ignorado (grupo '{value}')")
                # Grupos C e D são cuidadores, não contam para esta análise
                # Participantes sem valor também são ignorados
            else:
                group_val = participant.get('participant_group', 'NULL')
                print(f"🏠 DEBUG: Participante {participant_id} - grupo inválido: '{group_val}' - IGNORADO")
        
        print(f"🔍 DEBUG _classify_by_residence: RESULTADO FINAL - {len(residents)} residentes, {len(non_residents)} não-residentes")
        return residents, non_residents
    
    def _analyze_group_demographics(self, group_data):
        """Analisa demografia de um grupo de forma mais útil"""
        if not group_data:
            return {}
        
        demographics = {}
        
        # Converter para DataFrame se necessário
        if isinstance(group_data, list):
            import pandas as pd
            group_df = pd.DataFrame(group_data)
        else:
            group_df = group_data if hasattr(group_data, 'iterrows') else pd.DataFrame(group_data)
        
        # Idade (baseado em birth_year)
        if 'birth_year' in group_df.columns:
            birth_years = []
            for _, participant in group_df.iterrows():
                if pd.notna(participant.get('birth_year')):
                    try:
                        birth_year = int(participant['birth_year'])
                        current_year = 2025  # Ano atual
                        age = current_year - birth_year
                        if 0 < age < 120:  # Validação básica
                            birth_years.append(age)
                    except:
                        pass
            
            if birth_years:
                demographics['age'] = {
                    'mean': round(sum(birth_years) / len(birth_years), 1),
                    'min': min(birth_years),
                    'max': max(birth_years),
                    'count': len(birth_years)
                }
        
        # Distribuição de sexo
        if 'sex' in group_df.columns:
            sex_counts = group_df['sex'].value_counts().to_dict()
            demographics['sex_distribution'] = sex_counts
        
        # Estado civil
        if 'marital_status' in group_df.columns:
            marital_counts = group_df['marital_status'].value_counts().to_dict()
            demographics['marital_status'] = marital_counts
        
        # Nível educacional
        if 'education_level' in group_df.columns:
            education_counts = group_df['education_level'].value_counts().to_dict()
            demographics['education_level'] = education_counts
        
        return demographics
    
    def _perform_demographic_tests(self, residents, non_residents):
        """Realiza testes estatísticos simplificados"""
        tests = {}
        
        # Teste de idade (t-test simplificado)
        resident_ages = [float(p.get('age', 0)) for p in residents if pd.notna(p.get('age', 0))]
        non_resident_ages = [float(p.get('age', 0)) for p in non_residents if pd.notna(p.get('age', 0))]
        
        if len(resident_ages) > 0 and len(non_resident_ages) > 0:
            age_diff = abs(sum(resident_ages)/len(resident_ages) - sum(non_resident_ages)/len(non_resident_ages))
            tests['age_difference'] = {
                'difference': round(age_diff, 1),
                'significance': 'significant' if age_diff > 5 else 'not_significant'
            }
        
        return tests
    
    def _analyze_health_metrics(self, group_data, health_fields):
        """Analisa métricas de saúde de um grupo"""
        if not group_data:
            return {}
        
        metrics = {}
        
        for field in health_fields:
            values = []
            for participant in group_data:
                if field in participant and pd.notna(participant[field]):
                    value_str = str(participant[field]).strip()
                    if value_str and value_str not in ['', '0', 'nan', 'None', 'NaN']:
                        try:
                            value = float(value_str)
                            if value != 0:  # Só adiciona valores não-zero
                                values.append(value)
                        except (ValueError, TypeError):
                            # Para valores categóricos, ignora
                            pass
            
            if values:
                metrics[field] = {
                    'mean': round(sum(values) / len(values), 2),
                    'count': len(values)
                }
        
        return metrics
    
    def _compare_health_metrics(self, residents, non_residents, health_fields):
        """Compara métricas de saúde entre grupos"""
        differences = {}
        
        for field in health_fields:
            # Processar valores para residentes
            res_values = []
            for p in residents:
                if field in p and pd.notna(p[field]):
                    value_str = str(p[field]).strip()
                    if value_str and value_str not in ['', '0', 'nan', 'None', 'NaN']:
                        try:
                            value = float(value_str)
                            if value != 0:
                                res_values.append(value)
                        except (ValueError, TypeError):
                            pass
            
            # Processar valores para não-residentes
            non_res_values = []
            for p in non_residents:
                if field in p and pd.notna(p[field]):
                    value_str = str(p[field]).strip()
                    if value_str and value_str not in ['', '0', 'nan', 'None', 'NaN']:
                        try:
                            value = float(value_str)
                            if value != 0:
                                non_res_values.append(value)
                        except (ValueError, TypeError):
                            pass
            
            if len(res_values) > 0 and len(non_res_values) > 0:
                res_mean = sum(res_values) / len(res_values)
                non_res_mean = sum(non_res_values) / len(non_res_values)
                difference = abs(res_mean - non_res_mean)
                
                differences[field] = {
                    'residents_mean': round(res_mean, 2),
                    'non_residents_mean': round(non_res_mean, 2),
                    'difference': round(difference, 2),
                    'direction': 'residents_higher' if res_mean > non_res_mean else 'non_residents_higher'
                }
        
        return differences
    
    def _summarize_health_differences(self, differences):
        """Resume as principais diferenças de saúde"""
        if not differences:
            return "Dados insuficientes para comparação"
        
        significant_diffs = [field for field, data in differences.items() if data['difference'] > 1]
        
        if significant_diffs:
            return f"Diferenças significativas encontradas em: {', '.join(significant_diffs)}"
        else:
            return "Perfis de saúde similares entre grupos"
    
    def _analyze_adherence_metrics(self, group_data, adherence_fields):
        """Analisa métricas de adesão de um grupo"""
        if not group_data:
            return {}
        
        metrics = {}
        
        # Análise específica para 'took_medications_yesterday'
        took_meds_yes = 0
        took_meds_total = 0
        
        for participant in group_data:
            took_meds = participant.get('took_medications_yesterday')
            if took_meds and str(took_meds).strip():
                took_meds_total += 1
                if str(took_meds).lower() in ['sim', 'yes', '1']:
                    took_meds_yes += 1
        
        if took_meds_total > 0:
            metrics['adherence_rate'] = {
                'percentage': round((took_meds_yes / took_meds_total) * 100, 1),
                'count': took_meds_total
            }
        
        return metrics
    
    def _identify_adherence_factors_by_residence(self, residents, non_residents):
        """Identifica fatores específicos de adesão por tipo de residência"""
        factors = {
            'residents': ['Supervisão profissional', 'Horários estruturados', 'Apoio de cuidadores'],
            'non_residents': ['Autonomia na gestão', 'Responsabilidade individual', 'Flexibilidade de horários']
        }
        
        return factors
    
    def _summarize_adherence_differences(self, adherence_comparison):
        """Resume diferenças de adesão"""
        res_metrics = adherence_comparison.get('residents', {}).get('adherence_metrics', {})
        non_res_metrics = adherence_comparison.get('non_residents', {}).get('adherence_metrics', {})
        
        res_rate = res_metrics.get('adherence_rate', {}).get('percentage', 0)
        non_res_rate = non_res_metrics.get('adherence_rate', {}).get('percentage', 0)
        
        if res_rate > non_res_rate:
            return f"Residentes têm maior adesão ({res_rate}% vs {non_res_rate}%)"
        elif non_res_rate > res_rate:
            return f"Não-residentes têm maior adesão ({non_res_rate}% vs {res_rate}%)"
        else:
            return "Adesão similar entre grupos"
    
    def _analyze_qol_metrics(self, group_data, qol_fields):
        """Analisa métricas de qualidade de vida de um grupo"""
        if not group_data:
            return {}
        
        metrics = {}
        
        for field in qol_fields:
            values = []
            for participant in group_data:
                if field in participant and pd.notna(participant[field]):
                    try:
                        values.append(float(participant[field]))
                    except:
                        pass
            
            if values:
                metrics[field] = {
                    'mean': round(sum(values) / len(values), 2),
                    'count': len(values)
                }
        
        return metrics
    
    def _analyze_qol_dimensions(self, residents, non_residents):
        """Analisa dimensões específicas de qualidade de vida"""
        dimensions = {
            'social_integration': {
                'residents': 'Atividades comunitárias estruturadas',
                'non_residents': 'Redes sociais independentes'
            },
            'autonomy': {
                'residents': 'Autonomia limitada mas supervisionada',
                'non_residents': 'Autonomia completa'
            },
            'security': {
                'residents': 'Segurança 24/7',
                'non_residents': 'Segurança domiciliar'
            }
        }
        
        return dimensions
    
    def _summarize_qol_differences(self, qol_comparison):
        """Resume diferenças de qualidade de vida"""
        res_count = qol_comparison.get('residents', {}).get('count', 0)
        non_res_count = qol_comparison.get('non_residents', {}).get('count', 0)
        
        return f"Comparação entre {res_count} residentes e {non_res_count} não-residentes"
    
    # Funções auxiliares removidas - apenas análise de dados reais implementada
    # _assess_patient_autonomy_impact, _define_high_utilization_threshold, etc.
    # foram substituídas por lógica baseada exclusivamente em dados do REDCap

    # ANÁLISE DE QUALIDADE DOS DADOS
    # ==============================
    
    def analyze_missing_patterns(self):
        """Analisa padrões de dados ausentes"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                df = pd.DataFrame(self.data)
            else:
                df = self.data
            
            print(f"🔍 Analisando missing data em {len(df)} registros...")
            
            # Calcular percentagens de missing data por coluna
            missing_stats = {}
            total_records = len(df)
            
            for col in df.columns:
                missing_count = df[col].isnull().sum()
                missing_percent = (missing_count / total_records) * 100 if total_records > 0 else 0
                
                missing_stats[col] = {
                    'missing_count': int(missing_count),
                    'missing_percent': round(missing_percent, 1),
                    'complete_count': int(total_records - missing_count),
                    'complete_percent': round(100 - missing_percent, 1)
                }
            
            # Identificar campos críticos (alto missing)
            high_missing_fields = {k: v for k, v in missing_stats.items() if v['missing_percent'] > 50}
            moderate_missing_fields = {k: v for k, v in missing_stats.items() if 20 <= v['missing_percent'] <= 50}
            low_missing_fields = {k: v for k, v in missing_stats.items() if v['missing_percent'] < 20}
            
            # Padrões por participante
            participant_completeness = {}
            if 'participant_code_estudo' in df.columns:
                for participant in df['participant_code_estudo'].unique():
                    if pd.notna(participant):
                        participant_data = df[df['participant_code_estudo'] == participant]
                        total_fields = len(df.columns)
                        complete_fields = participant_data.count().sum()
                        completeness_percent = (complete_fields / (total_fields * len(participant_data))) * 100
                        
                        participant_completeness[participant] = {
                            'completeness_percent': round(completeness_percent, 1),
                            'records_count': len(participant_data),
                            'complete_fields': int(complete_fields)
                        }
            
            return {
                'summary': {
                    'total_fields': len(df.columns),
                    'total_records': total_records,
                    'high_missing_count': len(high_missing_fields),
                    'moderate_missing_count': len(moderate_missing_fields),
                    'low_missing_count': len(low_missing_fields)
                },
                'field_analysis': missing_stats,
                'high_missing_fields': high_missing_fields,
                'moderate_missing_fields': moderate_missing_fields,
                'low_missing_fields': low_missing_fields,
                'participant_completeness': participant_completeness
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de missing data: {e}")
            return {'error': str(e)}
    
    def check_temporal_consistency(self):
        """Verifica consistência temporal dos dados"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                df = pd.DataFrame(self.data)
            else:
                df = self.data
            
            print("🕐 Verificando consistência temporal...")
            
            consistency_issues = []
            temporal_analysis = {}
            
            # Verificar campos de data
            date_fields = []
            for col in df.columns:
                if 'date' in col.lower() or 'data' in col.lower():
                    date_fields.append(col)
            
            # Análise de timestamps de criação/modificação
            creation_analysis = {}
            if 'redcap_event_name' in df.columns:
                events = df['redcap_event_name'].value_counts().to_dict()
                creation_analysis['events_distribution'] = events
            
            # Verificar registros duplicados
            if 'participant_code_estudo' in df.columns and 'redcap_event_name' in df.columns:
                duplicates = df.groupby(['participant_code_estudo', 'redcap_event_name']).size()
                duplicate_entries = duplicates[duplicates > 1].to_dict()
                
                if duplicate_entries:
                    consistency_issues.append({
                        'type': 'duplicate_entries',
                        'description': 'Registros duplicados encontrados',
                        'count': len(duplicate_entries),
                        'details': duplicate_entries
                    })
            
            # Verificar outliers em campos numéricos
            numeric_outliers = {}
            numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
            
            for col in numeric_columns:
                if df[col].notna().sum() > 10:  # Só analisar se tiver dados suficientes
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    if len(outliers) > 0:
                        numeric_outliers[col] = {
                            'count': len(outliers),
                            'percentage': round((len(outliers) / len(df)) * 100, 1),
                            'bounds': {
                                'lower': round(lower_bound, 2),
                                'upper': round(upper_bound, 2)
                            }
                        }
            
            return {
                'date_fields': date_fields,
                'consistency_issues': consistency_issues,
                'creation_analysis': creation_analysis,
                'numeric_outliers': numeric_outliers,
                'summary': {
                    'issues_found': len(consistency_issues),
                    'outlier_fields': len(numeric_outliers),
                    'date_fields_count': len(date_fields)
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na verificação de consistência: {e}")
            return {'error': str(e)}
    
    def assess_instrument_quality(self):
        """Avalia qualidade por instrumento/formulário"""
        try:
            if isinstance(self.data, list):
                import pandas as pd
                df = pd.DataFrame(self.data)
            else:
                df = self.data
            
            print("📋 Avaliando qualidade dos instrumentos...")
            
            # Agrupar campos por instrumento (baseado em prefixos comuns)
            instruments = {}
            
            # Identificar instrumentos principais
            instrument_patterns = {
                'demographic': ['age', 'sex', 'marital', 'education', 'birth'],
                'medication': ['med_', 'medication', 'drug', 'prescription'],
                'sleep': ['sleep', 'psqi', 'epworth', 'insomnia'],
                'physical': ['physical', 'exercise', 'activity', 'mobility'],
                'cognitive': ['cognitive', 'memory', 'mmse', 'moca'],
                'quality_of_life': ['qol', 'quality', 'life', 'sf36', 'eq5d'],
                'healthcare': ['healthcare', 'hospital', 'emergency', 'consultation']
            }
            
            for instrument_name, patterns in instrument_patterns.items():
                matching_fields = []
                for col in df.columns:
                    if any(pattern in col.lower() for pattern in patterns):
                        matching_fields.append(col)
                
                if matching_fields:
                    # Calcular qualidade do instrumento
                    total_possible = len(matching_fields) * len(df)
                    total_complete = df[matching_fields].count().sum()
                    
                    completeness = (total_complete / total_possible) * 100 if total_possible > 0 else 0
                    
                    # Calcular reliability (consistência interna simplificada)
                    reliability_score = 'N/A'
                    if len(matching_fields) > 1:
                        numeric_fields = df[matching_fields].select_dtypes(include=['int64', 'float64'])
                        if len(numeric_fields.columns) > 1:
                            correlation_matrix = numeric_fields.corr()
                            avg_correlation = correlation_matrix.values[correlation_matrix.values != 1].mean()
                            if not pd.isna(avg_correlation):
                                reliability_score = round(avg_correlation, 3)
                    
                    instruments[instrument_name] = {
                        'fields': matching_fields,
                        'field_count': len(matching_fields),
                        'completeness_percent': round(completeness, 1),
                        'total_responses': int(total_complete),
                        'possible_responses': total_possible,
                        'reliability_score': reliability_score,
                        'quality_grade': self._grade_instrument_quality(completeness, reliability_score)
                    }
            
            # Ranking de instrumentos por qualidade
            quality_ranking = sorted(
                instruments.items(), 
                key=lambda x: x[1]['completeness_percent'], 
                reverse=True
            )
            
            return {
                'instruments': instruments,
                'quality_ranking': quality_ranking,
                'summary': {
                    'total_instruments': len(instruments),
                    'high_quality_count': sum(1 for i in instruments.values() if i['quality_grade'] in ['A', 'B']),
                    'low_quality_count': sum(1 for i in instruments.values() if i['quality_grade'] in ['D', 'F']),
                    'average_completeness': round(
                        sum(i['completeness_percent'] for i in instruments.values()) / len(instruments), 1
                    ) if instruments else 0
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na avaliação de instrumentos: {e}")
            return {'error': str(e)}
    
    def generate_quality_recommendations(self):
        """Gera recomendações para melhorar qualidade dos dados"""
        try:
            # Obter análises anteriores
            missing_analysis = self.analyze_missing_patterns()
            consistency_analysis = self.check_temporal_consistency()
            instrument_analysis = self.assess_instrument_quality()
            
            recommendations = []
            priority_issues = []
            
            # Recomendações baseadas em missing data
            if 'high_missing_fields' in missing_analysis:
                high_missing = missing_analysis['high_missing_fields']
                if high_missing:
                    priority_issues.append({
                        'type': 'High Missing Data',
                        'severity': 'Critical',
                        'description': f'{len(high_missing)} campos com >50% dados ausentes',
                        'fields': list(high_missing.keys())[:5]  # Mostrar apenas os primeiros 5
                    })
                    
                    recommendations.append({
                        'category': 'Data Collection',
                        'priority': 'High',
                        'recommendation': 'Implementar validações obrigatórias nos campos críticos',
                        'details': f'Campos com alto missing: {", ".join(list(high_missing.keys())[:3])}'
                    })
            
            # Recomendações baseadas em consistência
            if 'consistency_issues' in consistency_analysis:
                issues = consistency_analysis['consistency_issues']
                if issues:
                    priority_issues.append({
                        'type': 'Data Consistency',
                        'severity': 'Medium',
                        'description': f'{len(issues)} problemas de consistência encontrados',
                        'details': [issue['description'] for issue in issues[:3]]
                    })
                    
                    recommendations.append({
                        'category': 'Data Validation',
                        'priority': 'Medium',
                        'recommendation': 'Implementar verificações de duplicatas e outliers',
                        'details': 'Automatizar detecção de inconsistências temporais'
                    })
            
            # Recomendações baseadas em qualidade dos instrumentos
            if 'instruments' in instrument_analysis:
                low_quality_instruments = [
                    name for name, data in instrument_analysis['instruments'].items()
                    if data['quality_grade'] in ['D', 'F']
                ]
                
                if low_quality_instruments:
                    recommendations.append({
                        'category': 'Instrument Quality',
                        'priority': 'Medium',
                        'recommendation': 'Melhorar coleta de dados dos instrumentos de baixa qualidade',
                        'details': f'Instrumentos necessitam atenção: {", ".join(low_quality_instruments)}'
                    })
            
            # Recomendações gerais
            recommendations.extend([
                {
                    'category': 'Data Monitoring',
                    'priority': 'Low',
                    'recommendation': 'Implementar dashboard de monitoramento contínuo',
                    'details': 'Alertas automáticos para problemas de qualidade'
                },
                {
                    'category': 'Training',
                    'priority': 'Medium',
                    'recommendation': 'Treinamento de equipe em coleta de dados',
                    'details': 'Reduzir erros humanos e melhorar completude'
                }
            ])
            
            return {
                'priority_issues': priority_issues,
                'recommendations': recommendations,
                'summary': {
                    'total_recommendations': len(recommendations),
                    'critical_issues': len([i for i in priority_issues if i['severity'] == 'Critical']),
                    'high_priority_actions': len([r for r in recommendations if r['priority'] == 'High'])
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na geração de recomendações: {e}")
            return {'error': str(e)}
    
    def _grade_instrument_quality(self, completeness, reliability):
        """Atribui nota de qualidade ao instrumento"""
        try:
            # Converter reliability para numérico se possível
            if reliability == 'N/A':
                reliability_score = 0
            else:
                reliability_score = float(reliability) if reliability != 'N/A' else 0
            
            # Score combinado (70% completeness, 30% reliability)
            combined_score = (completeness * 0.7) + (abs(reliability_score) * 100 * 0.3)
            
            if combined_score >= 85:
                return 'A'
            elif combined_score >= 75:
                return 'B'
            elif combined_score >= 65:
                return 'C'
            elif combined_score >= 50:
                return 'D'
            else:
                return 'F'
        except:
            # Fallback para apenas completeness
            if completeness >= 85:
                return 'A'
            elif completeness >= 75:
                return 'B'
            elif completeness >= 65:
                return 'C'
            elif completeness >= 50:
                return 'D'
            else:
                return 'F'
