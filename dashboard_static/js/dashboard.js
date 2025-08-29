// Main Dashboard JavaScript
class RM4HealthDashboard {
    constructor() {
        this.data = null;
        this.charts = {};
        this.initialized = false;
    }

    async init() {
        try {
            console.log('Initializing RM4Health Dashboard...');
            
            // Mostrar loading
            this.showLoading();
            
            // Carregar dados
            this.data = await window.RM4HealthData.loadData();
            
            // Inicializar componentes
            this.updateStatistics();
            this.initializeCharts();
            this.updateParticipantsList();
            this.updateAlerts();
            this.setLastUpdateTime();
            
            // Mostrar dashboard
            this.showDashboard();
            
            this.initialized = true;
            console.log('Dashboard initialized successfully');
            
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            this.showError(error.message);
        }
    }

    showLoading() {
        document.getElementById('loadingContainer').classList.remove('d-none');
        document.getElementById('dashboardContent').classList.add('d-none');
        document.getElementById('errorContainer').classList.add('d-none');
    }

    showDashboard() {
        document.getElementById('loadingContainer').classList.add('d-none');
        document.getElementById('dashboardContent').classList.remove('d-none');
        document.getElementById('errorContainer').classList.add('d-none');
        
        // Adicionar animação
        document.getElementById('dashboardContent').classList.add('fade-in');
    }

    showError(message) {
        document.getElementById('loadingContainer').classList.add('d-none');
        document.getElementById('dashboardContent').classList.add('d-none');
        document.getElementById('errorContainer').classList.remove('d-none');
        document.getElementById('errorMessage').textContent = message;
    }

    updateStatistics() {
        const stats = this.data.statistics;
        
        // Atualizar cards estatísticos
        document.getElementById('totalParticipants').textContent = 
            stats.totalParticipants || 0;
        
        document.getElementById('averageAdherence').textContent = 
            `${stats.medicationAdherence?.percentage || 0}%`;
        
        document.getElementById('averageSleep').textContent = 
            stats.sleepQuality?.averagePSQI || '0.0';
        
        document.getElementById('healthAlerts').textContent = 
            stats.healthDeterioration?.totalAlerts || 0;
    }

    initializeCharts() {
        // Gráfico de tendência de aderência
        this.createAdherenceChart();
        
        // Gráfico de distribuição de idade
        this.createAgeDistributionChart();
    }

    createAdherenceChart() {
        const ctx = document.getElementById('adherenceChart');
        if (!ctx) return;

        const chartData = this.data.charts.adherenceTrend || {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            datasets: [{
                label: 'Aderência à Medicação (%)',
                data: [65, 70, 68, 75, 72, 78],
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                fill: true,
                tension: 0.4
            }]
        };

        this.charts.adherence = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: false
                    }
                },
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
                }
            }
        });
    }

    createAgeDistributionChart() {
        const ctx = document.getElementById('ageChart');
        if (!ctx) return;

        const ageData = this.data.charts.ageDistribution || {
            '18-30': 10,
            '31-50': 25,
            '51-65': 35,
            '65+': 20,
            'Não informado': 5
        };

        this.charts.age = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(ageData),
                datasets: [{
                    data: Object.values(ageData),
                    backgroundColor: [
                        '#0d6efd',
                        '#198754',
                        '#ffc107',
                        '#dc3545',
                        '#6c757d'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateParticipantsList() {
        const container = document.getElementById('highRiskParticipants');
        const participants = this.data.statistics.healthDeterioration?.highRiskParticipants || [];

        if (participants.length === 0) {
            container.innerHTML = '<p class="text-muted">Nenhum participante com alto risco detectado.</p>';
            return;
        }

        const html = participants.map(participant => `
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 rounded" 
                 style="background-color: #f8f9fa;">
                <div>
                    <strong>${participant.id}</strong>
                    <br>
                    <small class="text-muted">
                        ${participant.factors.slice(0, 2).join(', ')}
                        ${participant.factors.length > 2 ? '...' : ''}
                    </small>
                </div>
                <div class="text-end">
                    <span class="badge ${this.getRiskBadgeClass(participant.riskLevel)}">
                        ${participant.riskLevel}
                    </span>
                    <br>
                    <small class="text-muted">Score: ${participant.riskScore}</small>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    updateAlerts() {
        const container = document.getElementById('recentAlerts');
        const stats = this.data.statistics;
        
        const alerts = [];
        
        // Gerar alertas baseados nos dados
        if (stats.medicationAdherence?.percentage < 70) {
            alerts.push({
                type: 'warning',
                message: 'Aderência à medicação abaixo do esperado',
                time: '2 horas atrás'
            });
        }

        if (stats.sleepQuality?.averagePSQI > 10) {
            alerts.push({
                type: 'danger',
                message: 'Qualidade do sono crítica detectada',
                time: '4 horas atrás'
            });
        }

        if (stats.healthDeterioration?.totalAlerts > 5) {
            alerts.push({
                type: 'danger',
                message: `${stats.healthDeterioration.totalAlerts} participantes em alto risco`,
                time: '1 hora atrás'
            });
        }

        if (alerts.length === 0) {
            alerts.push({
                type: 'success',
                message: 'Nenhum alerta crítico no momento',
                time: 'Agora'
            });
        }

        const html = alerts.map(alert => `
            <div class="alert alert-${alert.type} alert-dismissible fade show mb-2" role="alert">
                <i class="fas fa-${this.getAlertIcon(alert.type)} me-2"></i>
                <strong>${alert.message}</strong>
                <br>
                <small class="text-muted">${alert.time}</small>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    getRiskBadgeClass(riskLevel) {
        switch (riskLevel) {
            case 'Alto': return 'bg-danger';
            case 'Médio': return 'bg-warning text-dark';
            default: return 'bg-success';
        }
    }

    getAlertIcon(type) {
        switch (type) {
            case 'danger': return 'exclamation-triangle';
            case 'warning': return 'exclamation-circle';
            case 'success': return 'check-circle';
            default: return 'info-circle';
        }
    }

    setLastUpdateTime() {
        const now = new Date();
        const timeString = now.toLocaleString('pt-PT', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const updateElement = document.getElementById('lastUpdate');
        if (updateElement) {
            updateElement.textContent = timeString;
        }
    }

    // Método para refresh dos dados
    async refresh() {
        if (!this.initialized) return;
        
        try {
            console.log('Refreshing dashboard data...');
            this.showLoading();
            
            // Recarregar dados
            this.data = await window.RM4HealthData.loadData();
            
            // Atualizar componentes
            this.updateStatistics();
            this.updateParticipantsList();
            this.updateAlerts();
            this.setLastUpdateTime();
            
            // Atualizar gráficos
            if (this.charts.adherence) {
                this.charts.adherence.destroy();
            }
            if (this.charts.age) {
                this.charts.age.destroy();
            }
            this.initializeCharts();
            
            this.showDashboard();
            
            console.log('Dashboard refreshed successfully');
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
            this.showError('Erro ao atualizar dados: ' + error.message);
        }
    }

    // Métodos utilitários
    exportData() {
        const dataStr = window.RM4HealthData.exportData('json');
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = 'rm4health-data-export.json';
        link.click();
        
        URL.revokeObjectURL(url);
    }
}

// Inicializar dashboard quando página carregar
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new RM4HealthDashboard();
    dashboard.init();
    
    // Tornar dashboard disponível globalmente
    window.dashboard = dashboard;
    
    // Auto-refresh a cada 5 minutos
    setInterval(() => {
        dashboard.refresh();
    }, 5 * 60 * 1000);
});

// Adicionar event listeners para interações
document.addEventListener('click', (e) => {
    // Refresh button
    if (e.target.id === 'refreshButton') {
        window.dashboard.refresh();
    }
    
    // Export button
    if (e.target.id === 'exportButton') {
        window.dashboard.exportData();
    }
});
