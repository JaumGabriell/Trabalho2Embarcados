// Charts.js - Gráficos do sistema

let membershipChart = null;
let simulationChart = null;

// Plota função de pertinência
function plotMembershipFunction(variable) {
    const canvas = document.getElementById('membershipChart');
    const ctx = canvas.getContext('2d');
    
    if (!membershipData || !membershipData[variable]) {
        return;
    }
    
    const data = membershipData[variable];
    const datasets = [];
    
    const colors = [
        '#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#6366f1'
    ];
    
    let colorIndex = 0;
    for (let term in data.terms) {
        datasets.push({
            label: term,
            data: data.terms[term],
            borderColor: colors[colorIndex % colors.length],
            backgroundColor: colors[colorIndex % colors.length] + '20',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        });
        colorIndex++;
    }
    
    if (membershipChart) {
        membershipChart.destroy();
    }
    
    membershipChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.universe.map((v, i) => i % 20 === 0 ? v.toFixed(1) : ''),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Funções de Pertinência - ${getVariableName(variable)}`,
                    font: { size: 16 }
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: getVariableUnit(variable)
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Grau de Pertinência'
                    },
                    min: 0,
                    max: 1
                }
            }
        }
    });
}

// Plota gráfico de simulação
// Variáveis para armazenar os gráficos
let tempComparisonChart = null;
let powerChart = null;
let errorChart = null;
let tempOutputChart = null;

function plotSimulationChart(results) {
    // Reduz pontos para melhor visualização (pega 1 a cada 10)
    const step = 10;
    const times = results.time.filter((_, i) => i % step === 0);
    const temps = results.temperature.filter((_, i) => i % step === 0);
    const powers = results.power_crac.filter((_, i) => i % step === 0);
    const setpoints = results.setpoint.filter((_, i) => i % step === 0);
    const errors = results.erro.filter((_, i) => i % step === 0);
    
    const labels = times.map(t => `${Math.floor(t/60)}h`);
    
    // Opções comuns para todos os gráficos
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    color: '#e2e8f0',
                    font: { size: 11 }
                }
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Tempo (horas)',
                    color: '#94a3b8'
                },
                ticks: { color: '#94a3b8' },
                grid: { color: '#334155' }
            },
            y: {
                ticks: { color: '#94a3b8' },
                grid: { color: '#334155' }
            }
        }
    };
    
    // 1. Gráfico: Temperatura Atual vs Setpoint
    if (tempComparisonChart) tempComparisonChart.destroy();
    const ctx1 = document.getElementById('tempComparisonChart').getContext('2d');
    tempComparisonChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperatura Atual',
                    data: temps,
                    borderColor: '#ef4444',
                    backgroundColor: '#ef444420',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Setpoint (22°C)',
                    data: setpoints,
                    borderColor: '#10b981',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    pointRadius: 0,
                    tension: 0
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Temperatura (°C)',
                        color: '#94a3b8'
                    },
                    min: 18,
                    max: 26
                }
            }
        }
    });
    
    // 2. Gráfico: Potência CRAC
    if (powerChart) powerChart.destroy();
    const ctx2 = document.getElementById('powerChart').getContext('2d');
    powerChart = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Potência CRAC',
                    data: powers,
                    borderColor: '#3b82f6',
                    backgroundColor: '#3b82f620',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Potência (%)',
                        color: '#94a3b8'
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
    
    // 3. Gráfico: Erro de Temperatura
    if (errorChart) errorChart.destroy();
    const ctx3 = document.getElementById('errorChart').getContext('2d');
    errorChart = new Chart(ctx3, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Erro (T_atual - Setpoint)',
                    data: errors,
                    borderColor: '#f59e0b',
                    backgroundColor: '#f59e0b20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Erro (°C)',
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
    
    // 4. Gráfico: Temperatura de Saída
    if (tempOutputChart) tempOutputChart.destroy();
    const ctx4 = document.getElementById('tempOutputChart').getContext('2d');
    tempOutputChart = new Chart(ctx4, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperatura de Saída',
                    data: temps,
                    borderColor: '#8b5cf6',
                    backgroundColor: '#8b5cf620',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Temperatura (°C)',
                        color: '#94a3b8'
                    },
                    min: 18,
                    max: 26
                }
            }
        }
    });
}

// Nomes das variáveis
function getVariableName(variable) {
    const names = {
        'erro': 'Erro de Temperatura',
        'delta_erro': 'Variação do Erro (Δe)',
        'temp_externa': 'Temperatura Externa',
        'carga_termica': 'Carga Térmica',
        'potencia_crac': 'Potência CRAC (Saída)'
    };
    return names[variable] || variable;
}

// Unidades das variáveis
function getVariableUnit(variable) {
    const units = {
        'erro': 'Erro (°C)',
        'delta_erro': 'Δe (°C)',
        'temp_externa': 'Temperatura (°C)',
        'carga_termica': 'Carga (%)',
        'potencia_crac': 'Potência (%)'
    };
    return units[variable] || '';
}
