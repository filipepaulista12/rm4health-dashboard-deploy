// Advanced Charts for RM4Health Dashboard
class RM4HealthCharts {
    constructor() {
        this.chartInstances = {};
        this.colorPalette = {
            primary: '#0d6efd',
            success: '#198754',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#0dcaf0',
            secondary: '#6c757d'
        };
    }

    // Gráfico de barras para aderência por medicação
    createMedicationAdherenceChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'bar',
            data: {
                labels: data.medications || ['Medicação A', 'Medicação B', 'Medicação C'],
                datasets: [{
                    label: 'Taxa de Aderência (%)',
                    data: data.adherenceRates || [85, 72, 91],
                    backgroundColor: this.colorPalette.primary,
                    borderColor: this.colorPalette.primary,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
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
        };

        return new Chart(ctx, config);
    }

    // Gráfico radar para PSQI
    createPSQIRadarChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'radar',
            data: {
                labels: [
                    'Qualidade Subjetiva',
                    'Latência do Sono',
                    'Duração do Sono',
                    'Eficiência do Sono',
                    'Distúrbios',
                    'Medicação',
                    'Disfunção Diurna'
                ],
                datasets: [{
                    label: 'PSQI Médio',
                    data: data.psqiComponents || [1.5, 2.0, 1.8, 1.2, 2.2, 0.8, 1.6],
                    backgroundColor: 'rgba(13, 110, 253, 0.2)',
                    borderColor: this.colorPalette.primary,
                    pointBackgroundColor: this.colorPalette.primary,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: this.colorPalette.primary
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                elements: {
                    line: {
                        borderWidth: 3
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 3,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Gráfico de linha para utilização de serviços
    createHealthcareUtilizationChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'line',
            data: {
                labels: data.months || ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                datasets: [
                    {
                        label: 'Consultas Programadas',
                        data: data.scheduledConsultations || [15, 18, 22, 19, 25, 21],
                        borderColor: this.colorPalette.success,
                        backgroundColor: 'rgba(25, 135, 84, 0.1)',
                        fill: false
                    },
                    {
                        label: 'Urgências',
                        data: data.emergencies || [5, 8, 3, 7, 4, 6],
                        borderColor: this.colorPalette.danger,
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        fill: false
                    },
                    {
                        label: 'Internamentos',
                        data: data.hospitalizations || [2, 1, 3, 2, 1, 2],
                        borderColor: this.colorPalette.warning,
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Mês'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Número de Utilizações'
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Gráfico de barras empilhadas para risco de deterioração
    createRiskDistributionChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'bar',
            data: {
                labels: ['Medicação', 'Sono', 'Serviços Saúde', 'Estado Geral'],
                datasets: [
                    {
                        label: 'Baixo Risco',
                        data: data.lowRisk || [45, 38, 42, 41],
                        backgroundColor: this.colorPalette.success
                    },
                    {
                        label: 'Risco Médio',
                        data: data.mediumRisk || [25, 32, 28, 29],
                        backgroundColor: this.colorPalette.warning
                    },
                    {
                        label: 'Alto Risco',
                        data: data.highRisk || [8, 12, 10, 9],
                        backgroundColor: this.colorPalette.danger
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Número de Participantes'
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Gráfico de scatter para correlações
    createCorrelationChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Aderência vs Qualidade do Sono',
                    data: data.correlationData || [
                        {x: 85, y: 6.2}, {x: 72, y: 7.8}, {x: 91, y: 5.1},
                        {x: 68, y: 8.5}, {x: 78, y: 6.9}, {x: 95, y: 4.8}
                    ],
                    backgroundColor: this.colorPalette.primary,
                    borderColor: this.colorPalette.primary
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Aderência à Medicação (%)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Score PSQI'
                        }
                    }
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Gráfico de área para tendências longitudinais
    createLongitudinalTrendChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'line',
            data: {
                labels: data.timePoints || ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4', 'Semana 5', 'Semana 6'],
                datasets: [
                    {
                        label: 'Aderência Média (%)',
                        data: data.adherenceTrend || [65, 70, 68, 75, 72, 78],
                        borderColor: this.colorPalette.primary,
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'PSQI Médio',
                        data: data.psqiTrend || [8.5, 8.2, 8.8, 7.9, 8.1, 7.6],
                        borderColor: this.colorPalette.warning,
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Tempo'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Aderência (%)',
                            color: this.colorPalette.primary
                        },
                        min: 0,
                        max: 100
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'PSQI Score',
                            color: this.colorPalette.warning
                        },
                        min: 0,
                        max: 21,
                        grid: {
                            drawOnChartArea: false,
                        },
                    },
                }
            }
        };

        return new Chart(ctx, config);
    }

    // Método para destruir um gráfico específico
    destroyChart(chartId) {
        if (this.chartInstances[chartId]) {
            this.chartInstances[chartId].destroy();
            delete this.chartInstances[chartId];
        }
    }

    // Método para destruir todos os gráficos
    destroyAllCharts() {
        Object.keys(this.chartInstances).forEach(chartId => {
            this.destroyChart(chartId);
        });
    }

    // Método utilitário para gerar cores aleatórias
    generateColors(count) {
        const colors = [];
        const baseColors = Object.values(this.colorPalette);
        
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        
        return colors;
    }

    // Método para atualizar dados de um gráfico existente
    updateChart(chartId, newData) {
        if (this.chartInstances[chartId]) {
            const chart = this.chartInstances[chartId];
            chart.data = newData;
            chart.update();
        }
    }

    // Método para redimensionar gráficos (útil para responsive)
    resizeCharts() {
        Object.values(this.chartInstances).forEach(chart => {
            chart.resize();
        });
    }
}

// Instância global dos gráficos
window.RM4HealthCharts = new RM4HealthCharts();

// Redimensionar gráficos quando janela muda de tamanho
window.addEventListener('resize', () => {
    window.RM4HealthCharts.resizeCharts();
});
