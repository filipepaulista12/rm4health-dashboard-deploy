# 📊 Extensões de Análise de Qualidade - RM4Health

## Funcionalidades Específicas para Artigo Científico

### 1. ANÁLISE DE QUALIDADE TEMPORAL
```python
def analyze_data_quality_temporal_patterns(self):
    """Analisa evolução da qualidade ao longo do tempo - ARTIGO"""
    temporal_quality = {
        'monthly_completeness': {},
        'weekly_patterns': {},
        'quality_deterioration_alerts': [],
        'seasonal_quality_trends': {}
    }
    
    # Agrupa por períodos temporais
    for record in self.data:
        # Analisa qualidade por período
        month = record.get('date_month')
        week = record.get('date_week')
        
        # Calcula scores de qualidade
        completeness_score = self._calculate_record_completeness(record)
        consistency_score = self._calculate_record_consistency(record)
        
        # Armazena por período
        if month:
            if month not in temporal_quality['monthly_completeness']:
                temporal_quality['monthly_completeness'][month] = []
            temporal_quality['monthly_completeness'][month].append(completeness_score)
    
    return temporal_quality

def calculate_data_quality_metrics_framework(self):
    """Framework completo de qualidade - 6 dimensões"""
    quality_framework = {
        'completeness': self._assess_completeness(),
        'accuracy': self._assess_accuracy(), 
        'consistency': self._assess_consistency(),
        'timeliness': self._assess_timeliness(),
        'validity': self._assess_validity(),
        'uniqueness': self._assess_uniqueness()
    }
    
    # Score geral baseado em pesos científicos
    weights = {
        'completeness': 0.25,
        'accuracy': 0.20,
        'consistency': 0.20,
        'timeliness': 0.15,
        'validity': 0.15,
        'uniqueness': 0.05
    }
    
    overall_score = sum(
        quality_framework[dim] * weights[dim] 
        for dim in weights.keys()
    )
    
    return {
        'dimensions': quality_framework,
        'overall_score': overall_score,
        'weights_used': weights,
        'grade': self._assign_quality_grade(overall_score)
    }
```

### 2. COMPLIANCE COM STANDARDS
```python
def assess_fair_principles_compliance(self):
    """Avalia compliance com princípios FAIR"""
    fair_assessment = {
        'findability': {
            'score': 0,
            'criteria': [
                'metadata_complete',
                'unique_identifiers',
                'searchable_fields'
            ]
        },
        'accessibility': {
            'score': 0,
            'criteria': [
                'data_available',
                'access_protocols',
                'authentication'
            ]
        },
        'interoperability': {
            'score': 0,
            'criteria': [
                'standard_formats',
                'controlled_vocabularies',
                'linked_data'
            ]
        },
        'reusability': {
            'score': 0,
            'criteria': [
                'rich_metadata',
                'clear_license',
                'provenance'
            ]
        }
    }
    
    # Calcula scores para cada princípio
    for principle, data in fair_assessment.items():
        principle_score = self._evaluate_fair_principle(principle, data['criteria'])
        fair_assessment[principle]['score'] = principle_score
    
    overall_fair_score = sum(p['score'] for p in fair_assessment.values()) / 4
    
    return {
        'principles': fair_assessment,
        'overall_fair_score': overall_fair_score,
        'compliance_level': self._classify_fair_compliance(overall_fair_score)
    }

def generate_quality_report_for_publication(self):
    """Gera relatório formatado para publicação científica"""
    report = {
        'study_overview': {
            'total_participants': len(set(r.get('participant_code') for r in self.data)),
            'total_records': len(self.data),
            'data_collection_period': self._get_collection_period(),
            'instruments_used': self._count_unique_instruments()
        },
        'quality_assessment': self.calculate_data_quality_metrics_framework(),
        'fair_compliance': self.assess_fair_principles_compliance(),
        'temporal_analysis': self.analyze_data_quality_temporal_patterns(),
        'recommendations': self._generate_publication_recommendations(),
        'limitations': self._identify_data_limitations()
    }
    
    return report
```

### 3. MISSING DATA ANALYSIS ADVANCED
```python
def analyze_missing_data_mechanisms(self):
    """Análise avançada de mecanismos de dados ausentes"""
    missing_analysis = {
        'mcar_test': {},  # Missing Completely At Random
        'mar_patterns': {},  # Missing At Random  
        'mnar_indicators': {},  # Missing Not At Random
        'informative_missingness': {}
    }
    
    # Little's MCAR test equivalent
    missing_patterns = self._identify_missing_patterns()
    
    # Análise por grupos demográficos
    demographic_missing = self._analyze_missing_by_demographics()
    
    # Temporal patterns
    temporal_missing = self._analyze_missing_temporal_patterns()
    
    return {
        'mechanisms': missing_analysis,
        'patterns': missing_patterns,
        'demographic_analysis': demographic_missing,
        'temporal_trends': temporal_missing,
        'recommendations': self._recommend_missing_data_handling()
    }
```