// Dashboard Principal RM4Health - VERSÃO CORRIGIDA
class RM4HealthDashboard {
    constructor() {
        this.isLoading = false;
        this.data = null;
        this.charts = {};
        this.initEventListeners();
    }

    initEventListeners() {
        // Event listeners para navegação
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetPage = e.target.getAttribute('href');
                if (targetPage && targetPage !== '#') {
                    this.navigateToPage(targetPage);
                }
            });
        });

        // Event listener para refresh
        const refreshBtn = document.getElementById('refreshData');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadData(true);
            });
        }
    }

    navigateToPage(page) {
        // Salvar estado antes de navegar
        if (this.data) {
            localStorage.setItem('rm4health_data', JSON.stringify(this.data));
        }
        
        // Navegar para a página
        window.location.href = page;
    }

    async init() {
        console.log(' Initializing RM4Health Dashboard...');
        
        // Mostrar loading
        this.showLoading();
        
        try {
            // Tentar carregar dados salvos primeiro
            const savedData = localStorage.getItem('rm4health_data');
            if (savedData && !this.isForceRefresh) {
                console.log(' Loading saved data from localStorage...');
                this.data = JSON.parse(savedData);
                await this.updateDashboard();
            } else {
                // Carregar dados do CSV
                await this.loadData();
            }
        } catch (error) {
            console.error(' Initialization error:', error);
            this.showError('Erro ao inicializar dashboard: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    async loadData(forceRefresh = false) {
        if (this.isLoading && !forceRefresh) {
            console.log(' Data loading already in progress...');
            return;
        }

        this.isLoading = true;
        this.showLoading();

        try {
            console.log(' Loading data from CSV...');
            
            // Verificar se RM4HealthData existe
            if (!window.RM4HealthData) {
                throw new Error('RM4HealthData não encontrado. Verifique se data-loader.js foi carregado.');
            }

            // Carregar dados
            this.data = await window.RM4HealthData.loadData();
            
            // Salvar no localStorage
            localStorage.setItem('rm4health_data', JSON.stringify(this.data));
            
            console.log(' Data loaded successfully:', this.data);
            
            // Atualizar dashboard
            await this.updateDashboard();
            
        } catch (error) {
            console.error(' Error loading data:', error);
            this.showError('Erro ao carregar dados: ' + error.message + '<br><small>Verifique se o arquivo CSV está acessível.</small>');
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    async updateDashboard() {
        console.log(' Updating dashboard with real data...');
        
        if (!this.data || !this.data.statistics) {
            throw new Error('Dados inválidos ou não carregados');
        }

        try {
            // Atualizar cards estatísticos
            this.updateStatCards();
            
            // Atualizar gráficos
            await this.updateCharts();
            
            // Atualizar tabela de alto risco
            this.updateHighRiskTable();
            
            // Atualizar timestamp
            this.updateTimestamp();
            
            console.log(' Dashboard updated successfully');
            
        } catch (error) {
            console.error(' Error updating dashboard:', error);
            throw error;
        }
    }

    updateStatCards() {
        const stats = this.data.statistics;
        
        // Card 1: Total de Participantes
        const totalCard = document.getElementById('totalParticipants');
        if (totalCard) {
            totalCard.textContent = stats.totalParticipants || 0;
        }

        // Card 2: Aderência à Medicação
        const adherenceCard = document.getElementById('medicationAdherence');
        const adherenceProgress = document.getElementById('adherenceProgress');
        if (adherenceCard && stats.medicationAdherence) {
            adherenceCard.textContent = `${stats.medicationAdherence.percentage}%`;
            if (adherenceProgress) {
                adherenceProgress.style.width = `${stats.medicationAdherence.percentage}%`;
                // Cor baseada na percentagem
                if (stats.medicationAdherence.percentage >= 80) {
                    adherenceProgress.className = 'progress-bar bg-success';
                } else if (stats.medicationAdherence.percentage >= 60) {
                    adherenceProgress.className = 'progress-bar bg-warning';
                } else {
                    adherenceProgress.className = 'progress-bar bg-danger';
                }
            }
        }

        // Card 3: Qualidade do Sono
        const sleepCard = document.getElementById('sleepQuality');
        if (sleepCard && stats.sleepQuality) {
            sleepCard.innerHTML = `
                <div class="fw-bold">${stats.sleepQuality.averagePSQI}</div>
                <small class="text-muted">${stats.sleepQuality.qualityLevel}</small>
            `;
        }

        // Card 4: Alertas de Saúde
        const alertsCard = document.getElementById('healthAlerts');
        const alertsBadge = document.getElementById('alertsBadge');
        if (alertsCard && stats.healthDeterioration) {
            alertsCard.textContent = stats.healthDeterioration.totalAlerts;
            if (alertsBadge) {
                alertsBadge.textContent = stats.healthDeterioration.totalAlerts;
                alertsBadge.className = stats.healthDeterioration.totalAlerts > 0 ? 
                    'badge bg-danger' : 'badge bg-success';
            }
        }

        console.log(' Stat cards updated with real data');
    }

    async updateCharts() {
        console.log(' Updating charts...');
        
        try {
            // Destruir gráficos existentes
            Object.values(this.charts).forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
            this.charts = {};

            // Verificar se Chart.js está disponível
            if (typeof Chart === 'undefined') {
                console.error(' Chart.js not loaded');
                document.querySelectorAll('.chart-container').forEach(container => {
                    container.innerHTML = '<div class="alert alert-warning">Chart.js não carregado</div>';
                });
                return;
            }

            // Gráfico 1: Distribuição Etária
            await this.createAgeDistributionChart();
            
            // Gráfico 2: Tendência de Aderência
            await this.createAdherenceTrendChart();
            
            console.log(' Charts updated successfully');
            
        } catch (error) {
            console.error(' Error updating charts:', error);
            document.querySelectorAll('.chart-container').forEach(container => {
                if (!container.innerHTML.includes('alert')) {
                    container.innerHTML = `<div class="alert alert-danger">Erro: ${error.message}</div>`;
                }
            });
        }
    }

    async createAgeDistributionChart() {
        const ageCanvas = document.getElementById('ageDistributionChart');
        if (!ageCanvas) {
            console.warn('Age distribution chart canvas not found');
            return;
        }

        const ctx = ageCanvas.getContext('2d');
        const ageData = this.data.charts?.ageDistribution || {
            '18-30': 0, '31-50': 0, '51-65': 0, '65+': 0, 'Não informado': 0
        };

        this.charts.ageDistribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(ageData),
                datasets: [{
                    data: Object.values(ageData),
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB', 
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Distribuição por Idade'
                    }
                }
            }
        });
    }

    async createAdherenceTrendChart() {
        const trendCanvas = document.getElementById('adherenceTrendChart');
        if (!trendCanvas) {
            console.warn('Adherence trend chart canvas not found');
            return;
        }

        const ctx = trendCanvas.getContext('2d');
        const trendData = this.data.charts?.adherenceTrend;

        if (trendData) {
            this.charts.adherenceTrend = new Chart(ctx, {
                type: 'line',
                data: trendData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Tendência de Aderência à Medicação'
                        }
                    }
                }
            });
        }
    }

    updateHighRiskTable() {
        const tableBody = document.getElementById('highRiskTableBody');
        if (!tableBody || !this.data.statistics.healthDeterioration) {
            console.warn('High risk table not found or no deterioration data');
            return;
        }

        const highRiskParticipants = this.data.statistics.healthDeterioration.highRiskParticipants || [];
        
        tableBody.innerHTML = '';

        if (highRiskParticipants.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted">
                        Nenhum participante de alto risco identificado
                    </td>
                </tr>
            `;
            return;
        }

        highRiskParticipants.forEach(participant => {
            const row = document.createElement('tr');
            
            const riskClass = participant.riskLevel === 'Alto' ? 'danger' : 
                             participant.riskLevel === 'Médio' ? 'warning' : 'info';
            
            row.innerHTML = `
                <td>
                    <strong>${participant.id}</strong>
                </td>
                <td>
                    <span class="badge bg-${riskClass}">
                        ${participant.riskLevel}
                    </span>
                </td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar bg-${riskClass}" 
                             style="width: ${participant.riskScore}%">
                            ${participant.riskScore}%
                        </div>
                    </div>
                </td>
                <td>
                    <small class="text-muted">
                        ${participant.factors.join(', ') || 'Sem fatores específicos'}
                    </small>
                </td>
            `;
            
            tableBody.appendChild(row);
        });

        console.log(' High risk table updated with', highRiskParticipants.length, 'participants');
    }

    updateTimestamp() {
        const timestampElement = document.getElementById('lastUpdate');
        if (timestampElement) {
            const now = new Date().toLocaleString('pt-PT');
            timestampElement.textContent = `Última atualização: ${now}`;
        }
    }

    showLoading() {
        const loadingElement = document.getElementById('loadingIndicator');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
        
        // Desabilitar botão de refresh
        const refreshBtn = document.getElementById('refreshData');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Carregando...';
        }
    }

    hideLoading() {
        const loadingElement = document.getElementById('loadingIndicator');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
        
        // Reabilitar botão de refresh
        const refreshBtn = document.getElementById('refreshData');
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Atualizar';
        }
    }

    showError(message) {
        // Remover alertas existentes
        document.querySelectorAll('.alert-custom').forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show alert-custom';
        alertDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Inserir no topo do container principal
        const mainContainer = document.querySelector('.container-fluid');
        if (mainContainer) {
            mainContainer.insertBefore(alertDiv, mainContainer.firstChild);
        }
        
        // Auto-remove após 10 segundos
        setTimeout(() => {
            alertDiv.remove();
        }, 10000);
    }

    // Método para debug
    debugInfo() {
        console.log(' Dashboard Debug Info:');
        console.log('Data:', this.data);
        console.log('Charts:', Object.keys(this.charts));
        console.log('Is Loading:', this.isLoading);
        return {
            data: this.data,
            charts: Object.keys(this.charts),
            isLoading: this.isLoading
        };
    }
}

// Inicialização global
document.addEventListener('DOMContentLoaded', async function() {
    console.log(' DOM loaded, initializing RM4Health Dashboard...');
    
    try {
        // Aguardar um pouco para garantir que todos os scripts carregaram
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Criar instância global do dashboard
        window.rm4Dashboard = new RM4HealthDashboard();
        
        // Inicializar
        await window.rm4Dashboard.init();
        
        console.log(' RM4Health Dashboard initialized successfully!');
        
    } catch (error) {
        console.error(' Failed to initialize dashboard:', error);
        
        // Mostrar erro na interface
        const container = document.querySelector('.container-fluid');
        if (container) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger mt-3';
            errorDiv.innerHTML = `
                <h4><i class="fas fa-exclamation-triangle"></i> Erro de Inicialização</h4>
                <p>Falha ao inicializar o dashboard: <strong>${error.message}</strong></p>
                <p class="mb-0">
                    <small>Verifique o console do navegador para mais detalhes.</small>
                </p>
            `;
            container.insertBefore(errorDiv, container.firstChild);
        }
    }
});

// Função global para debug
window.debugRM4Dashboard = () => {
    if (window.rm4Dashboard) {
        return window.rm4Dashboard.debugInfo();
    } else {
        console.log(' Dashboard not initialized');
        return null;
    }
};
