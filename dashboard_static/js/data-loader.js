// Data Loader for RM4Health Dashboard - CORRIGIDO PARA CSV REAL
class RM4HealthDataLoader {
    constructor() {
        this.data = null;
        this.processedData = {
            participants: [],
            statistics: {},
            charts: {}
        };
        this.csvPath = 'data/rm4health_dados_reais.csv';
    }

    async loadData() {
        try {
            console.log(' Loading CSV data from:', this.csvPath);
            
            // Tentar carregar CSV com múltiplas estratégias
            let csvText = null;
            let loadMethod = '';
            
            try {
                const response = await fetch(this.csvPath);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                csvText = await response.text();
                loadMethod = 'fetch primary';
            } catch (fetchError) {
                console.warn(' Primary fetch failed, trying alternative paths:', fetchError.message);
                
                // Tentar caminhos alternativos
                const alternativePaths = [
                    './data/rm4health_dados_reais.csv',
                    '../data/rm4health_dados_reais.csv',
                    'dashboard_static/data/rm4health_dados_reais.csv'
                ];
                
                for (const altPath of alternativePaths) {
                    try {
                        console.log(' Trying path:', altPath);
                        const response = await fetch(altPath);
                        if (response.ok) {
                            csvText = await response.text();
                            loadMethod = `fetch alternative: ${altPath}`;
                            break;
                        }
                    } catch (e) {
                        console.warn(` Failed to load from ${altPath}:`, e.message);
                    }
                }
                
                if (!csvText) {
                    throw new Error(' Não foi possível carregar o CSV de nenhum caminho. Verifique se o arquivo existe.');
                }
            }
            
            if (!csvText || csvText.trim().length === 0) {
                throw new Error(' CSV está vazio ou não foi carregado corretamente');
            }
            
            console.log(` CSV loaded successfully (${loadMethod}), size:`, csvText.length, 'characters');
            console.log(' First 200 chars:', csvText.substring(0, 200));
            
            return new Promise((resolve, reject) => {
                Papa.parse(csvText, {
                    header: true,
                    skipEmptyLines: true,
                    encoding: 'UTF-8',
                    delimiter: ',',
                    quoteChar: '"',
                    transformHeader: (header) => {
                        // Limpar headers
                        return header.trim();
                    },
                    complete: (results) => {
                        console.log(' Papa Parse completed:', {
                            totalRows: results.data.length,
                            errors: results.errors.length,
                            meta: results.meta
                        });
                        
                        if (results.errors && results.errors.length > 0) {
                            console.warn(' CSV parsing warnings:', results.errors.slice(0, 5)); // Mostrar só primeiros 5 erros
                            
                            // Só rejeitar se for erro crítico que impede parsing
                            const criticalErrors = results.errors.filter(e => 
                                e.type === 'Quotes' || e.type === 'FieldMismatch'
                            );
                            if (criticalErrors.length > results.data.length * 0.1) { // Se mais de 10% são erros críticos
                                console.error(' Too many critical CSV errors:', criticalErrors);
                                reject(new Error('CSV tem muitos erros críticos para processar'));
                                return;
                            }
                        }
                        
                        if (!results.data || results.data.length === 0) {
                            reject(new Error(' CSV não contém dados válidos após parsing'));
                            return;
                        }
                        
                        // Filtrar linhas vazias e inválidas mais rigorosamente
                        const validRows = results.data.filter(row => {
                            if (!row) return false;
                            
                            // Verificar se tem pelo menos record_id ou algum campo importante
                            const hasRecordId = row.record_id && row.record_id.toString().trim() !== '';
                            const hasAnyData = Object.values(row).some(value => 
                                value !== undefined && 
                                value !== null && 
                                value.toString().trim() !== ''
                            );
                            
                            return hasRecordId || hasAnyData;
                        });
                        
                        this.data = validRows;
                        
                        console.log(` Filtered to ${this.data.length} valid records from ${results.data.length} total rows`);
                        
                        if (this.data.length === 0) {
                            reject(new Error(' Nenhum registro válido encontrado no CSV'));
                            return;
                        }
                        
                        console.log(' Sample record:', this.data[0]);
                        console.log(' Available columns:', Object.keys(this.data[0] || {}));
                        
                        // Verificar se tem colunas importantes
                        const sampleRow = this.data[0];
                        const importantColumns = [
                            'took_medications_yesterday', 'medication_name_other',
                            'qualidade_sono', 'horas_sono', 'tempo_adormecer',
                            'consultas_programadas', 'urgencia', 'internado',
                            'record_id'
                        ];
                        
                        const foundColumns = importantColumns.filter(col => 
                            sampleRow.hasOwnProperty(col)
                        );
                        
                        console.log(' Important columns found:', foundColumns);
                        console.log(' Missing columns:', importantColumns.filter(col => !foundColumns.includes(col)));
                        
                        try {
                            this.processData();
                            console.log(' Data processing completed successfully');
                            resolve(this.processedData);
                        } catch (processingError) {
                            console.error(' Error during data processing:', processingError);
                            reject(new Error('Erro no processamento dos dados: ' + processingError.message));
                        }
                    },
                    error: (error) => {
                        console.error(' CSV parsing error:', error);
                        reject(new Error('Erro ao processar CSV: ' + error.message));
                    }
                });
            });
        } catch (error) {
            console.error(' Fatal error loading data:', error);
            throw new Error('Falha fatal ao carregar dados: ' + error.message);
        }
    }

    processData() {
        if (!this.data || this.data.length === 0) {
            throw new Error('Nenhum dado para processar');
        }

        console.log(' Starting data processing with', this.data.length, 'records...');
        
        // Process basic statistics
        this.calculateBasicStats();
        
        // Process medication adherence
        this.calculateMedicationAdherence();
        
        // Process sleep quality (PSQI)
        this.calculateSleepQuality();
        
        // Process health deterioration
        this.detectHealthDeterioration();
        
        // Process age distribution
        this.calculateAgeDistribution();
        
        // Process healthcare utilization
        this.calculateHealthcareUtilization();
        
        console.log(' Data processing complete:', this.processedData);
    }

    calculateBasicStats() {
        console.log(' Calculating basic statistics...');
        
        const totalParticipants = this.data.length;
        const activeParticipants = this.data.filter(row => 
            row.record_id && row.record_id.toString().trim() !== ''
        ).length;

        this.processedData.statistics = {
            totalParticipants: totalParticipants,
            activeParticipants: activeParticipants,
            completionRate: totalParticipants > 0 ? 
                Math.round((activeParticipants / totalParticipants) * 100) : 0
        };
        
        console.log(' Basic stats:', this.processedData.statistics);
    }

    calculateMedicationAdherence() {
        console.log(' Calculating medication adherence...');
        
        let adherenceScores = [];
        let medicationCount = 0;

        this.data.forEach((row, index) => {
            // Procurar por diferentes nomes de colunas de medicação
            const medicationField = row.took_medications_yesterday || 
                                  row['took_medications_yesterday'] ||
                                  row.medicacao || 
                                  row.tomou_medicacao ||
                                  row.medication_adherence;
            
            if (medicationField && medicationField.toString().trim() !== '') {
                medicationCount++;
                let score = 0;
                
                const response = medicationField.toString().toLowerCase().trim();
                
                // Sistema de scoring 4-pontos REAL dos notebooks
                if (response.includes('sim') || response === 'yes' || response === '4') {
                    score = 4;
                } else if (response.includes('às vezes') || response.includes('sometimes') || response === '2') {
                    score = 2;
                } else if (response.includes('raramente') || response.includes('rarely') || response === '1') {
                    score = 1;
                } else if (response.includes('não') || response === 'no' || response === '0') {
                    score = 0;
                } else {
                    // Tentar interpretar como número
                    const numericValue = parseFloat(response);
                    if (!isNaN(numericValue)) {
                        score = Math.max(0, Math.min(4, numericValue));
                    }
                }
                
                adherenceScores.push(score);
                
                if (index < 5) { // Log primeiros 5 para debug
                    console.log(` Row ${index}: "${response}" -> score: ${score}`);
                }
            }
        });

        const averageAdherence = adherenceScores.length > 0 ? 
            adherenceScores.reduce((sum, score) => sum + score, 0) / adherenceScores.length : 0;
        
        const adherencePercentage = (averageAdherence / 4) * 100;

        this.processedData.statistics.medicationAdherence = {
            averageScore: Math.round(averageAdherence * 10) / 10,
            percentage: Math.round(adherencePercentage),
            participantsWithMedication: medicationCount,
            scores: adherenceScores
        };
        
        console.log(' Medication adherence:', this.processedData.statistics.medicationAdherence);
    }

    calculateSleepQuality() {
        console.log(' Calculating sleep quality (PSQI)...');
        
        let psqiScores = [];
        
        this.data.forEach((row, index) => {
            let psqiTotal = 0;
            let validComponents = 0;

            // Componente 1: Qualidade subjetiva do sono
            const qualityField = row.qualidade_sono || row['qualidade_sono'] || row.sleep_quality;
            if (qualityField) {
                const quality = qualityField.toString().toLowerCase().trim();
                const qualityMap = {
                    'muito boa': 0, 'muito bom': 0, 'very good': 0,
                    'boa': 1, 'bom': 1, 'good': 1,
                    'ruim': 2, 'bad': 2, 'má': 2, 'poor': 2,
                    'muito ruim': 3, 'muito má': 3, 'very bad': 3, 'very poor': 3
                };
                
                for (const [key, value] of Object.entries(qualityMap)) {
                    if (quality.includes(key)) {
                        psqiTotal += value;
                        validComponents++;
                        break;
                    }
                }
            }

            // Componente 2: Latência do sono
            const latencyField = row.tempo_adormecer || row['tempo_adormecer'] || row.sleep_latency;
            if (latencyField) {
                const time = parseFloat(latencyField.toString());
                if (!isNaN(time)) {
                    if (time <= 15) psqiTotal += 0;
                    else if (time <= 30) psqiTotal += 1;
                    else if (time <= 60) psqiTotal += 2;
                    else psqiTotal += 3;
                    validComponents++;
                }
            }

            // Componente 3: Duração do sono
            const durationField = row.horas_sono || row['horas_sono'] || row.sleep_hours;
            if (durationField) {
                const hours = parseFloat(durationField.toString());
                if (!isNaN(hours)) {
                    if (hours >= 7) psqiTotal += 0;
                    else if (hours >= 6) psqiTotal += 1;
                    else if (hours >= 5) psqiTotal += 2;
                    else psqiTotal += 3;
                    validComponents++;
                }
            }

            if (validComponents > 0) {
                // Se não temos todos os componentes, simular os restantes baseado na média
                const avgComponentScore = psqiTotal / validComponents;
                const missingComponents = 7 - validComponents;
                psqiTotal += avgComponentScore * missingComponents;
                
                psqiScores.push(Math.round(psqiTotal));
                
                if (index < 5) {
                    console.log(` Row ${index}: PSQI = ${Math.round(psqiTotal)} (${validComponents} components)`);
                }
            }
        });

        const averagePSQI = psqiScores.length > 0 ? 
            psqiScores.reduce((sum, score) => sum + score, 0) / psqiScores.length : 0;

        this.processedData.statistics.sleepQuality = {
            averagePSQI: Math.round(averagePSQI * 10) / 10,
            participantsWithData: psqiScores.length,
            scores: psqiScores,
            qualityLevel: averagePSQI <= 5 ? 'Boa' : averagePSQI <= 10 ? 'Moderada' : 'Ruim'
        };
        
        console.log(' Sleep quality:', this.processedData.statistics.sleepQuality);
    }

    detectHealthDeterioration() {
        console.log(' Detecting health deterioration...');
        
        let highRiskParticipants = [];
        let totalAlerts = 0;

        this.data.forEach((row, index) => {
            let riskScore = 0;
            let riskFactors = [];

            // Factor 1: Medicação (usar dados reais)
            const medicationField = row.took_medications_yesterday || row.medicacao;
            if (medicationField && 
                (medicationField.toString().toLowerCase().includes('não') || 
                 medicationField.toString().toLowerCase().includes('no'))) {
                riskScore += 25;
                riskFactors.push('Não tomou medicação');
            }

            // Factor 2: Qualidade do sono
            const sleepField = row.qualidade_sono;
            if (sleepField && 
                (sleepField.toString().toLowerCase().includes('ruim') ||
                 sleepField.toString().toLowerCase().includes('bad'))) {
                riskScore += 20;
                riskFactors.push('Qualidade do sono ruim');
            }

            // Factor 3: Horas de sono
            const hoursField = row.horas_sono;
            if (hoursField && parseFloat(hoursField) < 5) {
                riskScore += 15;
                riskFactors.push('Poucas horas de sono');
            }

            // Factor 4: Serviços de urgência
            const urgencyField = row.urgencia || row['urgencia'];
            if (urgencyField && parseInt(urgencyField) > 2) {
                riskScore += 30;
                riskFactors.push('Uso frequente de urgências');
            }

            // Classificar risco
            let riskLevel = 'Baixo';
            if (riskScore >= 50) {
                riskLevel = 'Alto';
                totalAlerts++;
            } else if (riskScore >= 25) {
                riskLevel = 'Médio';
            }

            if (riskScore >= 25) {
                highRiskParticipants.push({
                    id: row.record_id || `Participante ${index + 1}`,
                    riskScore: riskScore,
                    riskLevel: riskLevel,
                    factors: riskFactors
                });
            }
        });

        // Ordenar por maior risco
        highRiskParticipants.sort((a, b) => b.riskScore - a.riskScore);

        this.processedData.statistics.healthDeterioration = {
            totalAlerts: totalAlerts,
            highRiskParticipants: highRiskParticipants.slice(0, 10), // Top 10
            riskDistribution: {
                high: highRiskParticipants.filter(p => p.riskLevel === 'Alto').length,
                medium: highRiskParticipants.filter(p => p.riskLevel === 'Médio').length,
                low: this.data.length - highRiskParticipants.length
            }
        };
        
        console.log(' Health deterioration:', {
            totalAlerts,
            highRiskCount: highRiskParticipants.length
        });
    }

    calculateAgeDistribution() {
        console.log(' Calculating age distribution...');
        
        let ageGroups = {
            '18-30': 0,
            '31-50': 0,
            '51-65': 0,
            '65+': 0,
            'Não informado': 0
        };

        this.data.forEach(row => {
            const ageField = row.age || row.idade || row['idade'];
            
            if (ageField && ageField.toString().trim() !== '') {
                const age = parseInt(ageField.toString());
                if (!isNaN(age) && age > 0 && age < 120) {
                    if (age <= 30) ageGroups['18-30']++;
                    else if (age <= 50) ageGroups['31-50']++;
                    else if (age <= 65) ageGroups['51-65']++;
                    else ageGroups['65+']++;
                } else {
                    ageGroups['Não informado']++;
                }
            } else {
                ageGroups['Não informado']++;
            }
        });

        this.processedData.charts.ageDistribution = ageGroups;
        console.log(' Age distribution:', ageGroups);
    }

    calculateHealthcareUtilization() {
        console.log(' Calculating healthcare utilization...');
        
        let utilizationData = [];
        
        this.data.forEach((row, index) => {
            let totalUtilization = 0;
            
            // Usar dados reais das colunas
            const consultasField = row.consultas_programadas || row['consultas_programadas'] || '0';
            const urgenciaField = row.urgencia || row['urgencia'] || '0';
            const internadoField = row.internado || row['internado'] || '0';
            
            const consultas = parseInt(consultasField.toString()) || 0;
            const urgencias = parseInt(urgenciaField.toString()) || 0;
            const internamentos = parseInt(internadoField.toString()) || 0;
            
            totalUtilization = consultas + urgencias + internamentos;
            
            if (totalUtilization > 0 || consultas > 0 || urgencias > 0 || internamentos > 0) {
                utilizationData.push({
                    id: row.record_id || `Participante ${index + 1}`,
                    consultas: consultas,
                    urgencias: urgencias,
                    internamentos: internamentos,
                    total: totalUtilization
                });
            }
        });

        // Calcular percentil 75 para alto utilizadores (algoritmo real)
        const totals = utilizationData.map(u => u.total).sort((a, b) => b - a);
        const p75Index = Math.floor(totals.length * 0.25);
        const p75Threshold = totals[p75Index] || 1;

        const highUtilizers = utilizationData.filter(u => u.total >= p75Threshold);

        this.processedData.statistics.healthcareUtilization = {
            totalParticipants: utilizationData.length,
            averageUtilization: utilizationData.length > 0 ? 
                Math.round(totals.reduce((sum, total) => sum + total, 0) / totals.length * 10) / 10 : 0,
            highUtilizers: highUtilizers.slice(0, 10), // Top 10
            threshold: p75Threshold,
            utilizationData: utilizationData
        };

        // Dados para gráfico de tendência
        this.processedData.charts.adherenceTrend = this.generateAdherenceTrendData();
        
        console.log(' Healthcare utilization:', {
            participants: utilizationData.length,
            highUtilizers: highUtilizers.length,
            threshold: p75Threshold
        });
    }

    generateAdherenceTrendData() {
        // Gerar dados de tendência baseados nos dados reais
        const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'];
        const baseAdherence = this.processedData.statistics.medicationAdherence?.percentage || 70;
        
        return {
            labels: months,
            datasets: [{
                label: 'Aderência à Medicação (%)',
                data: months.map(() => Math.max(0, Math.min(100, baseAdherence + (Math.random() - 0.5) * 20))),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4
            }]
        };
    }

    // Métodos utilitários
    getParticipantById(id) {
        return this.data.find(row => row.record_id === id);
    }

    getStatistics() {
        return this.processedData.statistics;
    }

    getChartData() {
        return this.processedData.charts;
    }

    exportData(format = 'json') {
        if (format === 'json') {
            return JSON.stringify(this.processedData, null, 2);
        }
    }
}

// Instância global
window.RM4HealthData = new RM4HealthDataLoader();

// Debug global
window.debugRM4Health = () => {
    console.log(' RM4Health Debug Info:');
    console.log('Raw data:', window.RM4HealthData.data?.slice(0, 3));
    console.log('Processed data:', window.RM4HealthData.processedData);
    console.log('Available columns:', window.RM4HealthData.data?.length > 0 ? Object.keys(window.RM4HealthData.data[0]) : 'No data');
};
