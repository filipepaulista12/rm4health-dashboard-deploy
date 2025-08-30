from flask import Flask, render_template, jsonify, request
import plotly.graph_objs as go
import plotly.utils
import json
from redcap_client import REDCapClient
from local_redcap_client import LocalREDCapClient
from data_processor import DataProcessor
from config import Config
import traceback
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rm4health_dashboard_secret_key'

# Inicializar cliente REDCap (local ou API)
if Config.USE_LOCAL_DATA:
    print("🔄 Inicializando cliente LOCAL...")
    redcap = LocalREDCapClient()
    print("✅ Cliente local inicializado")
else:
    print("🔄 Inicializando cliente API...")
    redcap = REDCapClient()
    print("✅ Cliente API inicializado")

# Cache para dados (simples cache em memória)
cached_data = {
    'data': None,
    'last_update': None,
    'cache_duration': 300  # 5 minutos
}

def get_cached_data():
    """Retorna dados em cache ou busca novos se necessário"""
    now = datetime.now()
    
    # Verifica se precisa atualizar cache
    if (cached_data['data'] is None or 
        cached_data['last_update'] is None or 
        (now - cached_data['last_update']).seconds > cached_data['cache_duration']):
        
        print("🔄 Atualizando cache de dados...")
        data = redcap.get_records()
        cached_data['data'] = data
        cached_data['last_update'] = now
        
    return cached_data['data']

@app.route('/')
def dashboard():
    """Dashboard principal"""
    try:
        print("🏠 Carregando dashboard principal...")
        
        # Buscar dados
        data = get_cached_data()
        processor = DataProcessor(data)
        
        # Estatísticas básicas
        stats = processor.get_basic_stats()
        stats.update({
            'project_name': Config.PROJECT_NAME,
            'project_title': Config.PROJECT_TITLE,
            'project_subtitle': Config.PROJECT_SUBTITLE,
            'last_update': cached_data['last_update'].strftime('%H:%M:%S') if cached_data['last_update'] else 'N/A'
        })
        
        # Gráficos básicos
        charts = generate_basic_charts(processor)
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             charts=charts,
                             success=bool(data))
    
    except Exception as e:
        print(f"❌ Erro no dashboard: {e}")
        traceback.print_exc()
        return render_template('dashboard.html', 
                             stats={'error': str(e)},
                             charts={},
                             success=False)

@app.route('/participants')
def participants():
    """Página de participantes"""
    try:
        data = get_cached_data()
        processor = DataProcessor(data)
        
        # Lista de participantes únicos
        participants_data = []
        participant_records = {}
        
        # Agrupa registros por participante
        for record in data:
            # Procura pelo campo correto de identificação
            participant_id = None
            for id_field in ['participant_code', 'record_id', 'participant_code_estudo']:
                if id_field in record and record[id_field]:
                    participant_id = record[id_field]
                    break
                    
            if participant_id:
                if participant_id not in participant_records:
                    participant_records[participant_id] = []
                participant_records[participant_id].append(record)
        
        # Calcula estatísticas por participante
        for participant_id, records in participant_records.items():
            total_fields = 0
            filled_fields = 0
            
            all_fields = set()
            for record in records:
                all_fields.update(record.keys())
            
            for record in records:
                for field in all_fields:
                    total_fields += 1
                    if field in record and record[field] not in [None, '', 'NaN', '']:
                        filled_fields += 1
            
            completion_rate = (filled_fields / total_fields * 100) if total_fields > 0 else 0
            
            participants_data.append({
                'id': participant_id,
                'records_count': len(records),
                'completion_rate': round(completion_rate, 1)
            })
        
        # Ordena por completude
        participants_data.sort(key=lambda x: x['completion_rate'], reverse=True)
        
        return render_template('participants.html', 
                             participants=participants_data[:50])  # Limita a 50 para performance
    
    except Exception as e:
        print(f"❌ Erro na página de participantes: {e}")
        return render_template('error.html', error=str(e))

@app.route('/data-explorer')
def data_explorer():
    """Explorador de dados"""
    try:
        data = get_cached_data()
        processor = DataProcessor(data)
        
        # Lista de colunas
        columns = processor.get_all_columns()
        
        return render_template('data_explorer.html', 
                             columns=columns,
                             total_columns=len(columns))
    
    except Exception as e:
        print(f"❌ Erro no explorador de dados: {e}")
        return render_template('error.html', error=str(e))

def generate_basic_charts(processor):
    """Gera gráficos básicos"""
    charts = {}
    
    try:
        # Gráfico de distribuição de idade
        age_data = processor.get_age_distribution()
        if age_data:
            age_fig = go.Figure(data=[
                go.Histogram(
                    x=age_data['data'], 
                    nbinsx=15, 
                    name='Distribuição de Idade',
                    marker_color=Config.PRIMARY_COLOR,
                    opacity=0.7
                )
            ])
            age_fig.update_layout(
                title='Distribuição de Idade dos Participantes',
                xaxis_title='Idade (anos)',
                yaxis_title='Frequência',
                height=Config.CHART_HEIGHT,
                template='plotly_white'
            )
            charts['age_distribution'] = json.dumps(age_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Gráfico de distribuição de gênero
        gender_data = processor.get_gender_distribution()
        if gender_data:
            gender_fig = go.Figure(data=[
                go.Pie(
                    labels=gender_data['labels'],
                    values=gender_data['values'],
                    name='Distribuição de Gênero',
                    marker_colors=[Config.PRIMARY_COLOR, Config.SECONDARY_COLOR]
                )
            ])
            gender_fig.update_layout(
                title='Distribuição de Gênero',
                height=Config.CHART_HEIGHT,
                template='plotly_white'
            )
            charts['gender_distribution'] = json.dumps(gender_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Gráfico de registros por participante
        records_data = processor.get_records_per_participant()
        if records_data:
            records_fig = go.Figure(data=[
                go.Bar(
                    x=records_data['labels'][:10], 
                    y=records_data['values'][:10],
                    name='Registros por Participante',
                    marker_color=Config.SECONDARY_COLOR
                )
            ])
            records_fig.update_layout(
                title='Top 10 - Registros por Participante',
                xaxis_title='ID do Participante',
                yaxis_title='Número de Registros',
                height=Config.CHART_HEIGHT,
                template='plotly_white'
            )
            charts['records_per_participant'] = json.dumps(records_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Gráfico de completude por instrumento
        completion_data = processor.get_completion_by_instrument()
        if completion_data:
            instruments = [item['instrument'] for item in completion_data[:10]]
            rates = [item['completion_rate'] for item in completion_data[:10]]
            
            completion_fig = go.Figure(data=[
                go.Bar(
                    x=rates,
                    y=instruments,
                    orientation='h',
                    name='Taxa de Completude',
                    marker_color=Config.PRIMARY_COLOR
                )
            ])
            completion_fig.update_layout(
                title='Taxa de Completude por Instrumento',
                xaxis_title='Taxa de Completude (%)',
                yaxis_title='Instrumento',
                height=max(Config.CHART_HEIGHT, len(instruments) * 40),
                template='plotly_white'
            )
            charts['completion_by_instrument'] = json.dumps(completion_fig, cls=plotly.utils.PlotlyJSONEncoder)
        
    except Exception as e:
        print(f"❌ Erro ao gerar gráficos: {e}")
        traceback.print_exc()
    
    return charts

@app.route('/api/data')
def api_data():
    """API endpoint para dados"""
    try:
        data = get_cached_data()
        processor = DataProcessor(data)
        
        return jsonify({
            'success': True,
            'stats': processor.get_basic_stats(),
            'data': data[:100] if data else [],  # Limita a 100 registros
            'total_records': len(data) if data else 0,
            'columns': processor.get_all_columns()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/column/<column_name>')
def api_column_summary(column_name):
    """API endpoint para resumo de coluna específica"""
    try:
        data = get_cached_data()
        processor = DataProcessor(data)
        summary = processor.get_column_summary(column_name)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/test-connection')
def api_test_connection():
    """API endpoint para testar conexão"""
    try:
        success = redcap.test_connection()
        return jsonify({
            'success': success,
            'message': 'Conexão testada com sucesso!' if success else 'Falha na conexão'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/analytics')
def analytics():
    """Página de análises avançadas"""
    try:
        data = get_cached_data()
        processor = DataProcessor(data)
        
        # Buscar metadados
        metadata = redcap.get_metadata() if redcap else None
        
        # Análises avançadas
        advanced_analytics = processor.get_advanced_analytics(metadata)
        
        return render_template('analytics.html', 
                             analytics=advanced_analytics,
                             success=True)
    
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        traceback.print_exc()
        return render_template('analytics.html', 
                             analytics={},
                             success=False,
                             error=str(e))

@app.route('/instruments')
def instruments():
    """Página de análise por instrumentos"""
    try:
        data = get_cached_data()
        processor = DataProcessor(data)
        metadata = redcap.get_metadata() if redcap else None
        
        advanced_analytics = processor.get_advanced_analytics(metadata)
        instruments_data = advanced_analytics.get('by_instrument', {})
        
        return render_template('instruments.html', 
                             instruments=instruments_data,
                             success=True)
    
    except Exception as e:
        print(f"❌ Erro nos instrumentos: {e}")
        return render_template('instruments.html', 
                             instruments={},
                             success=False,
                             error=str(e))

@app.route('/groups')
def groups():
    """Página de análise por grupos"""
    try:
        data = get_cached_data()
        processor = DataProcessor(data)
        metadata = redcap.get_metadata() if redcap else None
        
        advanced_analytics = processor.get_advanced_analytics(metadata)
        groups_data = advanced_analytics.get('by_group', {})
        
        return render_template('groups.html', 
                             groups=groups_data,
                             success=True)
    
    except Exception as e:
        print(f"❌ Erro nos grupos: {e}")
        return render_template('groups.html', 
                             groups={},
                             success=False,
                             error=str(e))

@app.route('/api/filter', methods=['POST'])
def api_filter_data():
    """API para filtrar dados"""
    try:
        filters = request.get_json() or {}
        data = get_cached_data()
        processor = DataProcessor(data)
        
        filtered_data = processor.filter_data(filters)
        filtered_processor = DataProcessor(filtered_data)
        
        stats = filtered_processor.get_basic_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'total_records': len(filtered_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/field/<field_name>')
def api_field_analysis(field_name):
    """API para análise de campo específico"""
    try:
        data = get_cached_data()
        processor = DataProcessor(data)
        
        analysis = processor.get_field_analysis(field_name)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/patterns')
def patterns():
    """Página de identificação de padrões"""
    try:
        data = get_cached_data()
        processor = DataProcessor(data)
        metadata = redcap.get_metadata() if redcap else None
        
        advanced_analytics = processor.get_advanced_analytics(metadata)
        patterns_data = advanced_analytics.get('patterns', {})
        insights = advanced_analytics.get('insights', [])
        
        return render_template('patterns.html', 
                             patterns=patterns_data,
                             insights=insights,
                             success=True)
    
    except Exception as e:
        print(f"❌ Erro nos padrões: {e}")
        return render_template('patterns.html', 
                             patterns={},
                             insights=[],
                             success=False,
                             error=str(e))

@app.route('/longitudinal')
def longitudinal_analysis():
    try:
        print("🔄 Iniciando análise longitudinal...")
        data = redcap.get_records()
        processor = DataProcessor(data)
        
        # Análises temporais
        temporal_trends = processor.analyze_temporal_trends()
        participant_trajectories = processor.get_health_trajectories()
        seasonal_patterns = processor.detect_seasonal_patterns()
        deterioration_alerts = processor.detect_health_deterioration()
        
        print("✅ Análise longitudinal concluída")
        return render_template('longitudinal.html',
                             trends=temporal_trends,
                             trajectories=participant_trajectories,
                             seasonal=seasonal_patterns,
                             alerts=deterioration_alerts,
                             success=True)
    except Exception as e:
        print(f"❌ Erro na análise longitudinal: {e}")
        return render_template('longitudinal.html',
                             trends={},
                             trajectories={},
                             seasonal={},
                             alerts={},
                             success=False,
                             error=str(e))

@app.route('/alerts')
def clinical_alerts():
    try:
        print("🚨 Iniciando análise de alertas clínicos...")
        data = redcap.get_records()
        processor = DataProcessor(data)
        
        # Sistema de alertas
        risk_participants = processor.identify_risk_participants()
        medication_alerts = processor.generate_medication_alerts()
        sleep_alerts = processor.analyze_critical_sleep()
        anomaly_alerts = processor.detect_response_anomalies()
        
        print("✅ Análise de alertas concluída")
        return render_template('alerts.html',
                             risk_participants=risk_participants,
                             medication_alerts=medication_alerts,
                             sleep_alerts=sleep_alerts,
                             anomalies=anomaly_alerts,
                             success=True)
    except Exception as e:
        print(f"❌ Erro nos alertas clínicos: {e}")
        return render_template('alerts.html',
                             risk_participants={},
                             medication_alerts={},
                             sleep_alerts={},
                             anomalies={},
                             success=False,
                             error=str(e))

@app.route('/medication-adherence')
def medication_adherence():
    try:
        print("💊 Iniciando análise de adesão medicamentosa...")
        data = redcap.get_records()
        processor = DataProcessor(data)
        
        # Análises de adesão
        adherence_rates = processor.calculate_adherence_rates()
        adherence_factors = processor.analyze_adherence_factors()
        adverse_effects = processor.analyze_adverse_effects()
        temporal_patterns = processor.medication_temporal_patterns()
        
        print("✅ Análise de adesão concluída")
        return render_template('medication_adherence.html',
                             rates=adherence_rates,
                             factors=adherence_factors,
                             adverse_effects=adverse_effects,
                             patterns=temporal_patterns,
                             success=True)
    except Exception as e:
        print(f"❌ Erro na análise de adesão: {e}")
        return render_template('medication_adherence.html',
                             rates={},
                             factors={},
                             adverse_effects={},
                             patterns={},
                             success=False,
                             error=str(e))

@app.route('/sleep-analysis')
def sleep_analysis():
    try:
        print("😴 Iniciando análise do sono...")
        data = redcap.get_records()
        processor = DataProcessor(data)
        
        # Análises do sono - FUNÇÕES NOVAS E INDEPENDENTES
        psqi_components = processor.analyze_psqi_components_rm4health()
        sleep_profiles = processor.create_sleep_profiles_rm4health()
        sleep_correlations = processor.sleep_symptom_correlations_rm4health()
        medication_impact = processor.medication_sleep_impact_rm4health()
        
        print("✅ Análise do sono concluída")
        return render_template('sleep_analysis.html',
                             components=psqi_components,
                             profiles=sleep_profiles,
                             correlations=sleep_correlations,
                             medication_impact=medication_impact,
                             success=True)
    except Exception as e:
        print(f"❌ Erro na análise do sono: {e}")
        return render_template('sleep_analysis.html',
                             components={},
                             profiles={},
                             correlations={},
                             medication_impact={},
                             success=False,
                             error=str(e))

@app.route('/healthcare-utilization')
def healthcare_utilization():
    """Página de análise de utilização de serviços de saúde"""
    try:
        # Obter dados do REDCap
        df = redcap.get_records()
        if not df:
            raise Exception("Não foi possível obter dados do REDCap")
        
        # Inicializar processador de dados
        processor = DataProcessor(df)
        
        # Executar análises de utilização
        service_patterns = processor.analyze_service_utilization_rm4health()
        cost_analysis = processor.calculate_cost_effectiveness_rm4health()
        remote_impact = processor.assess_remote_monitoring_impact_rm4health()
        utilization_predictors = processor.identify_utilization_predictors_rm4health()
        
        return render_template('healthcare_utilization.html',
                             patterns=service_patterns,
                             costs=cost_analysis,
                             remote_impact=remote_impact,
                             predictors=utilization_predictors,
                             success=True)
    
    except Exception as e:
        print(f"❌ Erro na análise de utilização de serviços: {e}")
        import traceback
        traceback.print_exc()
        return render_template('healthcare_utilization.html',
                             patterns={},
                             costs={},
                             remote_impact={},
                             predictors={},
                             success=False,
                             error=str(e))

@app.route('/caregivers')
def caregiver_analysis():
    """Página de análise de cuidadores"""
    try:
        # Obter dados do REDCap
        df = redcap.get_records()
        if not df:
            raise Exception("Não foi possível obter dados do REDCap")
        
        # Inicializar processador de dados
        processor = DataProcessor(df)
        
        # Executar análises de cuidadores
        caregiver_comparison = processor.compare_caregiver_groups()
        burden_analysis = processor.analyze_caregiver_burden()
        support_effectiveness = processor.assess_support_effectiveness()
        response_patterns = processor.caregiver_response_patterns()
        
        return render_template('caregivers.html',
                             comparison=caregiver_comparison,
                             burden=burden_analysis,
                             effectiveness=support_effectiveness,
                             patterns=response_patterns,
                             success=True)
    
    except Exception as e:
        print(f"❌ Erro na análise de cuidadores: {e}")
        import traceback
        traceback.print_exc()
        return render_template('caregivers.html',
                             comparison={},
                             burden={},
                             effectiveness={},
                             patterns={},
                             success=False,
                             error=str(e))

@app.route('/residence-comparison')
def residence_comparison():
    """Análise comparativa entre residentes e não-residentes"""
    try:
        print("🏠 Carregando análise residencial...")
        
        # Buscar dados
        data = get_cached_data()
        processor = DataProcessor(data)
        
        # Análises por tipo de residência
        demographic_comparison = processor.compare_residence_demographics()
        health_outcomes = processor.compare_health_outcomes()
        adherence_comparison = processor.compare_adherence_by_residence()
        quality_of_life = processor.compare_quality_of_life()
        
        print("✅ Análise residencial concluída!")
        
        return render_template('residence_comparison_fixed.html',
                             demographics=demographic_comparison,
                             health=health_outcomes,
                             adherence=adherence_comparison,
                             quality=quality_of_life,
                             success=True)
    
    except Exception as e:
        print(f"❌ Erro na análise residencial: {e}")
        import traceback
        traceback.print_exc()
        return render_template('residence_comparison_fixed.html',
                             demographics={},
                             health={},
                             adherence={},
                             quality={},
                             success=False,
                             error=str(e))

@app.route('/data-quality')
def data_quality_analysis():
    """Análise de qualidade dos dados do REDCap"""
    try:
        print("🔍 Carregando análise de qualidade dos dados...")
        
        # Buscar dados
        data = get_cached_data()
        processor = DataProcessor(data)
        
        # Análises de qualidade
        missing_patterns = processor.analyze_missing_patterns()
        consistency_check = processor.check_temporal_consistency()
        instrument_quality = processor.assess_instrument_quality()
        recommendations = processor.generate_quality_recommendations()
        
        print("✅ Análise de qualidade concluída!")
        
        return render_template('data_quality.html',
                             missing=missing_patterns,
                             consistency=consistency_check,
                             quality=instrument_quality,
                             recommendations=recommendations,
                             success=True,
                             error=None)
    except Exception as e:
        print(f"❌ Erro na análise de qualidade: {e}")
        return render_template('data_quality.html',
                             missing={},
                             consistency={},
                             quality={},
                             recommendations={},
                             success=False,
                             error=str(e))

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Página não encontrada'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error='Erro interno do servidor'), 500

if __name__ == '__main__':
    print("🏥 Iniciando RM4Health Dashboard...")
    print(f"🔗 URL da API: {Config.REDCAP_URL}")
    print(f"🎯 Token: {Config.REDCAP_TOKEN[:10]}...")
    print("🚀 Testando conexão...")
    
    # Teste inicial
    if redcap.test_connection():
        print("✅ Conexão OK! Iniciando servidor...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Falha na conexão! Verifique as credenciais.")
        print("🔄 Iniciando servidor mesmo assim...")
        app.run(debug=True, host='0.0.0.0', port=5000)
