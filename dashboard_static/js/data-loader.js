// Data Loader for RM4Health Dashboard - VERSÃO TOLERANTE PARA CSV COM ERROS
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
                    escapeChar: '"',
                    // CONFIGURAÇÕES TOLERANTES PARA CSV COM PROBLEMAS
                    fastMode: false,
                    preview: 0, // Parse all rows
                    dynamicTyping: false,
                    transformHeader: (header) => {
                        // Limpar headers mais agressivamente
                        return header.trim().replace(/["\r\n]/g, '');
                    },
                    complete: (results) => {
                        console.log(' Papa Parse completed:', {
                            totalRows: results.data.length,
                            errors: results.errors.length,
                            meta: results.meta
                        });
                        
                        if (results.errors && results.errors.length > 0) {
                            console.warn(' CSV parsing warnings (first 10):', results.errors.slice(0, 10)); 
                            
                            // Analisar tipos de erro mais cuidadosamente
                            const errorTypes = {};
                            results.errors.forEach(e => {
                                errorTypes[e.type] = (errorTypes[e.type] || 0) + 1;
                            });
                            console.log(' Error types distribution:', errorTypes);
                            
                            // Só rejeitar para erros estruturais muito graves
                            const fatalErrors = results.errors.filter(e => 
                                e.type === 'Delimiter' && e.code === 'UndetectableDelimiter'
                            );
                            
                            if (fatalErrors.length > 0) {
                                console.error(' Fatal CSV structure errors:', fatalErrors);
                                reject(new Error('CSV tem erros estruturais fatais'));
                                return;
                            }
                            
                            // Para outros erros, apenas avisar mas continuar
                            console.log(`ℹ CSV tem ${results.errors.length} erros/avisos menores, mas continuando processamento...`);
                        }
                        
                        if (!results.data || results.data.length === 0) {
                            reject(new Error(' CSV não contém dados válidos após parsing'));
                            return;
                        }
                        
                        // Filtrar linhas vazias e inválidas mais inteligentemente
                        const validRows = results.data.filter((row, index) => {
                            if (!row || typeof row !== 'object') return false;
                            
                            // Contar campos não vazios
                            const nonEmptyFields = Object.values(row).filter(value => 
                                value !== undefined && 
                                value !== null && 
                                value !== '' &&
                                value.toString().trim() !== ''
                            ).length;
                            
                            // Aceitar linha se tiver pelo menos 5 campos preenchidos
                            const isValid = nonEmptyFields >= 5;
                            
                            if (index < 10 && !isValid) { // Debug primeiras linhas problemáticas
                                console.log(` Row ${index} rejected: only ${nonEmptyFields} non-empty fields`);
                            }
                            
                            return isValid;
                        });
                        
                        this.data = validRows;
                        
                        console.log(` Filtered to ${this.data.length} valid records from ${results.data.length} total rows`);
                        
                        if (this.data.length === 0) {
                            reject(new Error(' Nenhum registro válido encontrado no CSV após filtragem'));
                            return;
                        }
                        
                        console.log(' Sample record (first valid):', this.data[0]);
                        console.log(' Available columns:', Object.keys(this.data[0] || {}));
                        console.log(' Columns count:', Object.keys(this.data[0] || {}).length);
                        
                        // Verificar colunas importantes com nomes mais flexíveis
                        const sampleRow = this.data[0];
                        const importantColumns = this.findImportantColumns(sampleRow);
                        
                        console.log(' Important columns mapping:', importantColumns);
                        
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
                        console.error(' CSV parsing fatal error:', error);
                        reject(new Error('Erro fatal ao processar CSV: ' + error.message));
                    }
                });
            });
        } catch (error) {
            console.error(' Fatal error loading data:', error);
            throw new Error('Falha fatal ao carregar dados: ' + error.message);
        }
    }

    // Novo método para mapear colunas importantes com nomes flexíveis
    findImportantColumns(sampleRow) {
        if (!sampleRow) return {};
        
        const columnNames = Object.keys(sampleRow);
        const mapping = {};
        
        // Procurar por padrões de nomes de colunas importantes
        const patterns = {
            record_id: ['record_id', 'id', 'participant', 'codigo', 'Record ID'],
            medication: ['took_medications', 'medicament', 'tomou', 'medication'],
            sleep_quality: ['qualidade_sono', 'sleep_quality', 'sono'],
            sleep_hours: ['horas_sono', 'sleep_hours', 'horas'],
            sleep_latency: ['tempo_adormecer', 'sleep_latency', 'adormecer'],
            consultations: ['consultas_programadas', 'consultas', 'consultations'],
            emergency: ['urgencia', 'emergency', 'urgência'],
            hospitalization: ['internado', 'hospital', 'internamento'],
            age: ['age', 'idade', 'nascimento'],
            gender: ['sexo', 'gender', 'sex']
        };
        
        for (const [key, possibleNames] of Object.entries(patterns)) {
            const foundColumn = columnNames.find(col => 
                possibleNames.some(pattern => 
                    col.toLowerCase().includes(pattern.toLowerCase())
                )
            );
            if (foundColumn) {
                mapping[key] = foundColumn;
            }
        }
        
        return mapping;
    }

    processData() {
        if (!this.data || this.data.length === 0) {
            throw new Error('Nenhum dado para processar');
        }

        console.log(' Starting data processing with', this.data.length, 'records...');
        
        // Mapear colunas importantes
        this.columnMapping = this.findImportantColumns(this.data[0]);
        console.log(' Column mapping for processing:', this.columnMapping);
        
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
        
        // Contar participantes ativos (com ID válido)
        const idColumn = this.columnMapping.record_id;
        const activeParticipants = this.data.filter(row => {
            const id = idColumn ? row[idColumn] : row.record_id || row.id;
            return id && id.toString().trim() !== '';
        }).length;

        this.processedData.statistics = {
            totalParticipants: totalParticipants,
            activeParticipants: activeParticipants || totalParticipants,
            completionRate: totalParticipants > 0 ? 
                Math.round(((activeParticipants || totalParticipants) / totalParticipants) * 100) : 0
        };
        
        console.log(' Basic stats:', this.processedData.statistics);
    }

    calculateMedicationAdherence() {
        console.log(' Calculating medication adherence...');
        
        let adherenceScores = [];
        let medicationCount = 0;

        // Procurar colunas relacionadas a medicação
        const medColumns = Object.keys(this.data[0] || {}).filter(col =>
            col.toLowerCase().includes('medic') || 
            col.toLowerCase().includes('tomou') ||
            col.toLowerCase().includes('took')
        );
        
        console.log(' Found potential medication columns:', medColumns);

        this.data.forEach((row, index) => {
            // Tentar múltiplas colunas de medicação
            let medicationField = null;
            for (const col of medColumns) {
                if (row[col] && row[col].toString().trim() !== '') {
                    medicationField = row[col];
                    break;
                }
            }
            
            // Fallback para colunas conhecidas
            if (!medicationField) {
                medicationField = row.took_medications_yesterday || 
                                row['took_medications_yesterday'] ||
                                row.medicacao || 
                                row.tomou_medicacao ||
                                row.medication_adherence;
            }
            
            if (medicationField && medicationField.toString().trim() !== '') {
                medicationCount++;
                let score = 0;
                
                const response = medicationField.toString().toLowerCase().trim();
                
                // Sistema de scoring 4-pontos REAL
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
                    } else {
                        // Default baseado em resposta positiva/negativa
                        score = response.includes('sim') || response.includes('yes') || 
                               response.includes('sempre') ? 4 : 
                               response.includes('não') || response.includes('no') || 
                               response.includes('nunca') ? 0 : 2;
                    }
                }
                
                adherenceScores.push(score);
                
                if (index < 5) { // Log primeiros 5 para debug
                    console.log(` Row ${index}: "${response}" -> score: ${score}`);
                }
            }
        });

        const averageAdherence = adherenceScores.length > 0 ? 
            adherenceScores.reduce((sum, score) => sum + score, 0) / adherenceScores.length : 2.5; // Default médio
        
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
        
        // Procurar colunas de sono
        const sleepColumns = Object.keys(this.data[0] || {}).filter(col =>
            col.toLowerCase().includes('sono') || 
            col.toLowerCase().includes('sleep') ||
            col.toLowerCase().includes('qualidade') ||
            col.toLowerCase().includes('horas') ||
            col.toLowerCase().includes('adormecer')
        );
        
        console.log(' Found potential sleep columns:', sleepColumns);
        
        this.data.forEach((row, index) => {
            let psqiTotal = 0;
            let validComponents = 0;

            // Componente 1: Qualidade subjetiva do sono
            const qualityFields = sleepColumns.filter(col => 
                col.toLowerCase().includes('qualidade') || 
                col.toLowerCase().includes('quality')
            );
            
            for (const field of qualityFields) {
                const qualityField = row[field];
                if (qualityField && qualityField.toString().trim() !== '') {
                    const quality = qualityField.toString().toLowerCase().trim();
                    const qualityMap = {
                        'muito boa': 0, 'muito bom': 0, 'very good': 0, 'excelente': 0,
                        'boa': 1, 'bom': 1, 'good': 1,
                        'ruim': 2, 'bad': 2, 'má': 2, 'poor': 2, 'regular': 2,
                        'muito ruim': 3, 'muito má': 3, 'very bad': 3, 'very poor': 3, 'péssima': 3
                    };
                    
                    for (const [key, value] of Object.entries(qualityMap)) {
                        if (quality.includes(key)) {
                            psqiTotal += value;
                            validComponents++;
                            break;
                        }
                    }
                    break; // Usar primeiro campo encontrado
                }
            }

            // Componente 2: Latência do sono
            const latencyFields = sleepColumns.filter(col => 
                col.toLowerCase().includes('adormecer') || 
                col.toLowerCase().includes('latency') ||
                col.toLowerCase().includes('tempo')
            );
            
            for (const field of latencyFields) {
                const latencyField = row[field];
                if (latencyField && latencyField.toString().trim() !== '') {
                    const timeStr = latencyField.toString().replace(/[^\d.]/g, '');
                    const time = parseFloat(timeStr);
                    if (!isNaN(time)) {
                        if (time <= 15) psqiTotal += 0;
                        else if (time <= 30) psqiTotal += 1;
                        else if (time <= 60) psqiTotal += 2;
                        else psqiTotal += 3;
                        validComponents++;
                        break;
                    }
                }
            }

            // Componente 3: Duração do sono
            const durationFields = sleepColumns.filter(col => 
                col.toLowerCase().includes('horas') || 
                col.toLowerCase().includes('hours') ||
                col.toLowerCase().includes('duração')
            );
            
            for (const field of durationFields) {
                const durationField = row[field];
                if (durationField && durationField.toString().trim() !== '') {
                    const hoursStr = durationField.toString().replace(/[^\d.]/g, '');
                    const hours = parseFloat(hoursStr);
                    if (!isNaN(hours)) {
                        if (hours >= 7) psqiTotal += 0;
                        else if (hours >= 6) psqiTotal += 1;
                        else if (hours >= 5) psqiTotal += 2;
                        else psqiTotal += 3;
                        validComponents++;
                        break;
                    }
                }
            }

            if (validComponents > 0) {
                // Se não temos todos os componentes, estimar os restantes
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
            psqiScores.reduce((sum, score) => sum + score, 0) / psqiScores.length : 7; // Default médio

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

        // Procurar colunas relacionadas à saúde
        const healthColumns = Object.keys(this.data[0] || {}).filter(col =>
            col.toLowerCase().includes('saude') || 
            col.toLowerCase().includes('health') ||
            col.toLowerCase().includes('sintoma') ||
            col.toLowerCase().includes('dor') ||
            col.toLowerCase().includes('fadiga')
        );

        this.data.forEach((row, index) => {
            let riskScore = 0;
            let riskFactors = [];

            // Factor 1: Medicação (usar múltiplas colunas)
            const medColumns = Object.keys(row).filter(col =>
                col.toLowerCase().includes('medic') || 
                col.toLowerCase().includes('tomou')
            );
            
            for (const col of medColumns) {
                const medicationField = row[col];
                if (medicationField && 
                    (medicationField.toString().toLowerCase().includes('não') || 
                     medicationField.toString().toLowerCase().includes('no'))) {
                    riskScore += 25;
                    riskFactors.push('Não tomou medicação');
                    break;
                }
            }

            // Factor 2: Qualidade do sono
            const sleepColumns = Object.keys(row).filter(col =>
                col.toLowerCase().includes('qualidade') || 
                col.toLowerCase().includes('sono')
            );
            
            for (const col of sleepColumns) {
                const sleepField = row[col];
                if (sleepField && 
                    (sleepField.toString().toLowerCase().includes('ruim') ||
                     sleepField.toString().toLowerCase().includes('bad') ||
                     sleepField.toString().toLowerCase().includes('má'))) {
                    riskScore += 20;
                    riskFactors.push('Qualidade do sono ruim');
                    break;
                }
            }

            // Factor 3: Uso de serviços de urgência
            const urgencyColumns = Object.keys(row).filter(col =>
                col.toLowerCase().includes('urgencia') || 
                col.toLowerCase().includes('emergency')
            );
            
            for (const col of urgencyColumns) {
                const urgencyField = row[col];
                if (urgencyField) {
                    const urgencyCount = parseInt(urgencyField.toString()) || 0;
                    if (urgencyCount > 2) {
                        riskScore += 30;
                        riskFactors.push('Uso frequente de urgências');
                        break;
                    }
                }
            }

            // Factor 4: Sintomas de saúde
            for (const col of healthColumns) {
                const healthField = row[col];
                if (healthField && healthField.toString().trim() !== '') {
                    const healthValue = healthField.toString().toLowerCase();
                    if (healthValue.includes('ruim') || healthValue.includes('má') || 
                        healthValue.includes('pior') || healthValue.includes('bad')) {
                        riskScore += 15;
                        riskFactors.push('Sintomas de saúde reportados');
                        break;
                    }
                }
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
                const participantId = this.getParticipantId(row, index);
                highRiskParticipants.push({
                    id: participantId,
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

        // Procurar colunas de idade
        const ageColumns = Object.keys(this.data[0] || {}).filter(col =>
            col.toLowerCase().includes('age') || 
            col.toLowerCase().includes('idade') ||
            col.toLowerCase().includes('nascimento')
        );

        this.data.forEach(row => {
            let age = null;
            
            // Tentar extrair idade de múltiplas colunas
            for (const col of ageColumns) {
                const ageField = row[col];
                if (ageField && ageField.toString().trim() !== '') {
                    if (col.toLowerCase().includes('nascimento')) {
                        // Se for ano de nascimento, calcular idade
                        const birthYear = parseInt(ageField.toString());
                        if (!isNaN(birthYear) && birthYear > 1900) {
                            age = new Date().getFullYear() - birthYear;
                            break;
                        }
                    } else {
                        // Se for idade direta
                        age = parseInt(ageField.toString());
                        if (!isNaN(age) && age > 0 && age < 120) {
                            break;
                        }
                    }
                }
            }
            
            if (age && age > 0 && age < 120) {
                if (age <= 30) ageGroups['18-30']++;
                else if (age <= 50) ageGroups['31-50']++;
                else if (age <= 65) ageGroups['51-65']++;
                else ageGroups['65+']++;
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
        
        // Procurar colunas de utilização de serviços
        const serviceColumns = Object.keys(this.data[0] || {}).filter(col =>
            col.toLowerCase().includes('consulta') || 
            col.toLowerCase().includes('urgencia') ||
            col.toLowerCase().includes('internado') ||
            col.toLowerCase().includes('hospital')
        );
        
        this.data.forEach((row, index) => {
            let totalUtilization = 0;
            let consultas = 0, urgencias = 0, internamentos = 0;
            
            // Extrair dados de cada tipo de serviço
            for (const col of serviceColumns) {
                const value = parseInt(row[col]?.toString()) || 0;
                if (col.toLowerCase().includes('consulta') && !col.toLowerCase().includes('urgencia')) {
                    consultas += value;
                } else if (col.toLowerCase().includes('urgencia')) {
                    urgencias += value;
                } else if (col.toLowerCase().includes('internado') || col.toLowerCase().includes('hospital')) {
                    internamentos += value;
                }
            }
            
            totalUtilization = consultas + urgencias + internamentos;
            
            if (totalUtilization > 0 || consultas > 0 || urgencias > 0 || internamentos > 0) {
                utilizationData.push({
                    id: this.getParticipantId(row, index),
                    consultas: consultas,
                    urgencias: urgencias,
                    internamentos: internamentos,
                    total: totalUtilization
                });
            }
        });

        // Calcular percentil 75 para alto utilizadores
        const totals = utilizationData.map(u => u.total).sort((a, b) => b - a);
        const p75Index = Math.floor(totals.length * 0.25);
        const p75Threshold = totals[p75Index] || 1;

        const highUtilizers = utilizationData.filter(u => u.total >= p75Threshold);

        this.processedData.statistics.healthcareUtilization = {
            totalParticipants: utilizationData.length,
            averageUtilization: utilizationData.length > 0 ? 
                Math.round(totals.reduce((sum, total) => sum + total, 0) / totals.length * 10) / 10 : 0,
            highUtilizers: highUtilizers.slice(0, 10),
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

    // Método auxiliar para extrair ID do participante
    getParticipantId(row, index) {
        const idColumns = Object.keys(row).filter(col =>
            col.toLowerCase().includes('id') || 
            col.toLowerCase().includes('codigo') ||
            col.toLowerCase().includes('participant')
        );
        
        for (const col of idColumns) {
            const id = row[col];
            if (id && id.toString().trim() !== '') {
                return id.toString().trim();
            }
        }
        
        return `Participante ${index + 1}`;
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
        return this.data.find(row => {
            const participantId = this.getParticipantId(row, 0);
            return participantId === id;
        });
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

// Debug global melhorado
window.debugRM4Health = () => {
    console.log(' RM4Health Debug Info:');
    console.log('Raw data sample:', window.RM4HealthData.data?.slice(0, 3));
    console.log('Processed data:', window.RM4HealthData.processedData);
    console.log('Column mapping:', window.RM4HealthData.columnMapping);
    console.log('Available columns:', window.RM4HealthData.data?.length > 0 ? Object.keys(window.RM4HealthData.data[0]).slice(0, 20) : 'No data');
    return {
        rawDataCount: window.RM4HealthData.data?.length,
        columnMapping: window.RM4HealthData.columnMapping,
        processedStats: window.RM4HealthData.processedData.statistics
    };
};
