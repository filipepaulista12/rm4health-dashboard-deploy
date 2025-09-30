"""
Módulo de análises avançadas para o dashboard RM4Health
Funcionalidades para identificar padrões e responder perguntas do estudo
"""
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json

class RM4HealthAnalytics:
    def __init__(self, records, metadata):
        self.records = records
        self.metadata = metadata
        self.field_labels = {field['field_name']: field['field_label'] 
                           for field in metadata}
        
    def analyze_by_instrument(self):
        """Análise por instrumento/formulário"""
        instruments = defaultdict(lambda: {
            'count': 0,
            'participants': set(),
            'fields_filled': defaultdict(int),
            'completion_rate': {}
        })
        
        for record in self.records:
            instrument = record.get('redcap_repeat_instrument', 'baseline')
            if not instrument:
                instrument = 'baseline'
                
            participant = record.get('participant_code')
            
            instruments[instrument]['count'] += 1
            if participant:
                instruments[instrument]['participants'].add(participant)
            
            # Contar campos preenchidos por instrumento
            for field, value in record.items():
                if value and str(value).strip():
                    instruments[instrument]['fields_filled'][field] += 1
        
        # Converter sets para listas para serialização JSON
        result = {}
        for instrument, data in instruments.items():
            result[instrument] = {
                'name': self._get_instrument_name(instrument),
                'total_records': data['count'],
                'unique_participants': len(data['participants']),
                'participants_list': list(data['participants']),
                'top_fields': dict(sorted(data['fields_filled'].items(), 
                                        key=lambda x: x[1], reverse=True)[:10])
            }
        
        return result
    
    def analyze_by_group(self):
        """Análise por grupos de participantes"""
        groups = defaultdict(lambda: {
            'participants': set(),
            'total_records': 0,
            'instruments': defaultdict(int),
            'demographics': defaultdict(int)
        })
        
        for record in self.records:
            group = record.get('participant_group', 'Não especificado')
            participant = record.get('participant_code')
            instrument = record.get('redcap_repeat_instrument', 'baseline')
            
            if not instrument:
                instrument = 'baseline'
            
            groups[group]['participants'].add(participant)
            groups[group]['total_records'] += 1
            groups[group]['instruments'][instrument] += 1
            
            # Análise demográfica básica
            if 'age' in record and record['age']:
                try:
                    age = int(record['age'])
                    if age < 65:
                        groups[group]['demographics']['<65 anos'] += 1
                    elif age < 75:
                        groups[group]['demographics']['65-74 anos'] += 1
                    else:
                        groups[group]['demographics']['75+ anos'] += 1
                except:
                    pass
        
        # Preparar resultado
        result = {}
        for group, data in groups.items():
            result[group] = {
                'total_participants': len(data['participants']),
                'total_records': data['total_records'],
                'participants_list': list(data['participants']),
                'instruments_distribution': dict(data['instruments']),
                'demographics': dict(data['demographics'])
            }
        
        return result
    
    def get_completion_rates(self):
        """Taxa de preenchimento por campo e instrumento"""
        completion = defaultdict(lambda: defaultdict(int))
        total_by_instrument = defaultdict(int)
        
        for record in self.records:
            instrument = record.get('redcap_repeat_instrument', 'baseline')
            if not instrument:
                instrument = 'baseline'
                
            total_by_instrument[instrument] += 1
            
            for field, value in record.items():
                if value and str(value).strip():
                    completion[instrument][field] += 1
        
        result = {}
        for instrument, fields in completion.items():
            result[instrument] = {}
            total = total_by_instrument[instrument]
            
            for field, count in fields.items():
                percentage = (count / total * 100) if total > 0 else 0
                result[instrument][field] = {
                    'filled': count,
                    'total': total,
                    'percentage': round(percentage, 1),
                    'label': self.field_labels.get(field, field)
                }
        
        return result
    
    def analyze_patterns(self):
        """Identificar padrões interessantes nos dados"""
        patterns = {
            'temporal_patterns': self._analyze_temporal_patterns(),
            'correlation_insights': self._analyze_correlations(),
            'completion_patterns': self._analyze_completion_patterns(),
            'group_differences': self._analyze_group_differences()
        }
        
        return patterns
    
    def _analyze_temporal_patterns(self):
        """Análise de padrões temporais"""
        patterns = {}
        
        # Análise por data de preenchimento
        date_fields = [field for field in self.field_labels.keys() 
                      if 'data' in field.lower() or 'date' in field.lower()]
        
        for date_field in date_fields:
            dates = []
            for record in self.records:
                if record.get(date_field):
                    try:
                        # Tentar diferentes formatos de data
                        date_str = record[date_field]
                        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                            try:
                                date_obj = datetime.strptime(date_str, fmt)
                                dates.append(date_obj)
                                break
                            except:
                                continue
                    except:
                        pass
            
            if dates:
                dates.sort()
                patterns[date_field] = {
                    'label': self.field_labels.get(date_field, date_field),
                    'total_entries': len(dates),
                    'date_range': {
                        'start': dates[0].strftime('%Y-%m-%d'),
                        'end': dates[-1].strftime('%Y-%m-%d')
                    },
                    'monthly_distribution': self._get_monthly_distribution(dates)
                }
        
        return patterns
    
    def _analyze_correlations(self):
        """Análise de correlações básicas"""
        correlations = {}
        
        # Campos numéricos para análise
        numeric_fields = []
        for field, label in self.field_labels.items():
            if any(term in label.lower() for term in ['idade', 'score', 'escala', 'pontuação']):
                numeric_fields.append(field)
        
        # Análise básica de correlações (simplificada)
        for field in numeric_fields[:5]:  # Limitar para evitar sobrecarga
            values = []
            for record in self.records:
                if record.get(field):
                    try:
                        value = float(record[field])
                        values.append(value)
                    except:
                        pass
            
            if len(values) > 5:
                correlations[field] = {
                    'label': self.field_labels.get(field, field),
                    'count': len(values),
                    'mean': round(sum(values) / len(values), 2) if values else 0,
                    'min': min(values) if values else 0,
                    'max': max(values) if values else 0
                }
        
        return correlations
    
    def _analyze_completion_patterns(self):
        """Padrões de preenchimento"""
        patterns = {}
        
        # Análise por participante
        participant_completion = defaultdict(int)
        participant_instruments = defaultdict(set)
        
        for record in self.records:
            participant = record.get('participant_code')
            instrument = record.get('redcap_repeat_instrument', 'baseline')
            
            if participant:
                # Contar campos preenchidos por participante
                filled_fields = sum(1 for v in record.values() if v and str(v).strip())
                participant_completion[participant] += filled_fields
                participant_instruments[participant].add(instrument)
        
        patterns['participant_engagement'] = {}
        for participant, total_fields in participant_completion.items():
            patterns['participant_engagement'][participant] = {
                'total_fields_filled': total_fields,
                'instruments_participated': len(participant_instruments[participant]),
                'instruments_list': list(participant_instruments[participant])
            }
        
        return patterns
    
    def _analyze_group_differences(self):
        """Diferenças entre grupos"""
        differences = {}
        
        groups = defaultdict(list)
        for record in self.records:
            group = record.get('participant_group', 'Não especificado')
            groups[group].append(record)
        
        # Comparar grupos
        for group, records in groups.items():
            differences[group] = {
                'total_records': len(records),
                'avg_fields_per_record': 0,
                'most_common_instruments': {}
            }
            
            total_fields = 0
            instruments = defaultdict(int)
            
            for record in records:
                filled_fields = sum(1 for v in record.values() if v and str(v).strip())
                total_fields += filled_fields
                
                instrument = record.get('redcap_repeat_instrument', 'baseline')
                instruments[instrument] += 1
            
            if records:
                differences[group]['avg_fields_per_record'] = round(total_fields / len(records), 1)
                differences[group]['most_common_instruments'] = dict(
                    sorted(instruments.items(), key=lambda x: x[1], reverse=True)[:3]
                )
        
        return differences
    
    def _get_monthly_distribution(self, dates):
        """Distribuição mensal de datas"""
        monthly = defaultdict(int)
        for date in dates:
            month_key = date.strftime('%Y-%m')
            monthly[month_key] += 1
        return dict(monthly)
    
    def _get_instrument_name(self, instrument_key):
        """Obter nome legível do instrumento"""
        instrument_names = {
            'baseline': 'Dados Baseline',
            'IV - Estado de saúde e diagnósticos prévios': 'Estado de Saúde',
            'V - Utilização dos serviços de saúde e eventos': 'Utilização de Serviços',
            'VI - Plano Terapêutico em vigor': 'Plano Terapêutico',
            'VII - Questionário de Pittsburgh sobre a Qualidade do Sono  (PSQI-PT)': 'Qualidade do Sono (PSQI)',
            'VIII  - Questionário de adesão à medicação, sintomas e bem-estar': 'Medicação e Bem-estar'
        }
        
        return instrument_names.get(instrument_key, instrument_key)
    
    def generate_insights(self):
        """Gerar insights automáticos dos dados"""
        insights = []
        
        # Análise por instrumentos
        instruments = self.analyze_by_instrument()
        if instruments:
            most_used = max(instruments.items(), key=lambda x: x[1]['total_records'])
            insights.append(f"📋 O instrumento mais utilizado é '{most_used[1]['name']}' com {most_used[1]['total_records']} registros")
        
        # Análise por grupos
        groups = self.analyze_by_group()
        if groups:
            largest_group = max(groups.items(), key=lambda x: x[1]['total_participants'])
            insights.append(f"👥 O maior grupo é '{largest_group[0]}' com {largest_group[1]['total_participants']} participantes")
        
        # Análise de preenchimento
        completion = self.get_completion_rates()
        avg_completion = []
        for instrument, fields in completion.items():
            if fields:
                avg = sum(field['percentage'] for field in fields.values()) / len(fields)
                avg_completion.append((instrument, avg))
        
        if avg_completion:
            best_completion = max(avg_completion, key=lambda x: x[1])
            insights.append(f"✅ O instrumento com melhor preenchimento é '{self._get_instrument_name(best_completion[0])}' ({best_completion[1]:.1f}%)")
        
        # Patterns analysis
        patterns = self.analyze_patterns()
        if 'participant_engagement' in patterns['completion_patterns'] and patterns['completion_patterns']['participant_engagement']:
            engagement = patterns['completion_patterns']['participant_engagement']
            if engagement:
                most_active = max(engagement.items(), key=lambda x: x[1]['total_fields_filled'])
                insights.append(f"🏆 Participante mais ativo: {most_active[0]} ({most_active[1]['total_fields_filled']} campos preenchidos)")
        
        return insights
