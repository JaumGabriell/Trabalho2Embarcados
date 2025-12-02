// Main JavaScript para o Sistema Fuzzy

let currentTab = 'erro';
let membershipData = null;

// Carrega funções de pertinência ao iniciar
document.addEventListener('DOMContentLoaded', function() {
    loadMembershipFunctions();
});

// Carrega dados das funções de pertinência
async function loadMembershipFunctions() {
    try {
        const response = await fetch('/api/membership_functions');
        const result = await response.json();
        
        if (result.success) {
            membershipData = result.data;
            // Plota o gráfico inicial sem passar evento
            plotMembershipFunction('erro');
        }
    } catch (error) {
        console.error('Erro ao carregar funções de pertinência:', error);
    }
}

// Calcula potência CRAC
async function calculate() {
    const erro = parseFloat(document.getElementById('erro').value);
    const delta_erro = parseFloat(document.getElementById('delta_erro').value);
    const temp_externa = parseFloat(document.getElementById('temp_externa').value);
    const carga_termica = parseFloat(document.getElementById('carga_termica').value);
    
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                erro: erro,
                delta_erro: delta_erro,
                temp_externa: temp_externa,
                carga_termica: carga_termica
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayOutput(result.potencia_crac);
            // displayInferenceDetails removido - seção de inferência foi substituída por gráficos
        } else {
            alert('Erro no cálculo: ' + result.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao calcular potência CRAC');
    }
}

// Exibe resultado
function displayOutput(power) {
    document.getElementById('output-value').textContent = power.toFixed(2);
    document.getElementById('power-bar-fill').style.width = power + '%';
}

// Exibe detalhes da inferência
function displayInferenceDetails(details) {
    if (!details) return;
    
    let html = '<h3>Valores Fuzzy das Entradas:</h3>';
    html += '<div class="metrics-grid">';
    
    // Mostra os valores fuzzy mais significativos
    for (let variable in details.fuzzy_values) {
        html += `<div class="metric"><strong>${variable}:</strong><br>`;
        for (let term in details.fuzzy_values[variable]) {
            const value = details.fuzzy_values[variable][term];
            if (value > 0.01) {
                html += `${term}: ${value.toFixed(3)}<br>`;
            }
        }
        html += '</div>';
    }
    html += '</div>';
    
    html += `<h3>Regras Ativadas: ${details.activated_rules_count}</h3>`;
    html += '<div class="message-container">';
    
    details.activated_rules.forEach((rule, i) => {
        html += `<div class="message-item">
            <strong>Regra ${i+1}:</strong> 
            Ativação: ${rule.activation.toFixed(3)}<br>
            IF Erro=${rule.conditions.erro} AND ΔErro=${rule.conditions.delta_erro} 
            AND TempExt=${rule.conditions.temp_externa} AND Carga=${rule.conditions.carga_termica}
            THEN Potência=${rule.output}
        </div>`;
    });
    
    html += '</div>';
    
    document.getElementById('inference-details').innerHTML = html;
}

// Muda aba de funções de pertinência
function showTab(tabName, event) {
    currentTab = tabName;
    
    // Atualiza botões
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Atualiza gráfico
    if (membershipData) {
        plotMembershipFunction(tabName);
    }
}

// Reseta inputs
function resetInputs() {
    document.getElementById('erro').value = 0;
    document.getElementById('delta_erro').value = 0;
    document.getElementById('temp_externa').value = 25;
    document.getElementById('carga_termica').value = 40;
    document.getElementById('output-value').textContent = '--';
    document.getElementById('power-bar-fill').style.width = '0%';
}

// Variáveis para controle da simulação
let simulationInterval = null;
let simulationData = [];

// Executa simulação de 24h
async function runSimulation() {
    const temp_inicial = parseFloat(document.getElementById('sim_temp_inicial').value);
    const temp_externa = parseFloat(document.getElementById('sim_temp_externa').value);
    const carga_base = parseFloat(document.getElementById('sim_carga_base').value);
    
    // Oculta o preview
    const preview = document.getElementById('simulation-preview');
    if (preview) preview.style.display = 'none';
    
    // Mostra loading com mensagem
    document.getElementById('simulation-results').innerHTML = `
        <div style="text-align: center; padding: 40px;">
            <div class="loading"></div>
            <h3 style="margin-top: 20px; color: #2196F3;">Iniciando simulação de 24 horas...</h3>
            <p style="color: #666;">Os dados estão sendo enviados via MQTT</p>
            <div class="metric" style="margin-top: 20px;">
                <div class="metric-value" id="simulation-progress">0%</div>
                <div class="metric-label">Progresso</div>
            </div>
            <div class="metric" style="margin-top: 10px;">
                <div class="metric-value" id="simulation-points">0</div>
                <div class="metric-label">Pontos Recebidos</div>
            </div>
        </div>
    `;
    document.getElementById('simulation-results').style.display = 'block';
    
    try {
        // Limpa dados anteriores
        simulationData = [];
        
        // Inicia a simulação (não aguarda resultados)
        const response = await fetch('/api/simulation/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                temp_inicial: temp_inicial,
                temp_externa_base: temp_externa,
                carga_base: carga_base
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Inicia polling para receber dados via MQTT
            startSimulationPolling();
        } else {
            document.getElementById('simulation-results').innerHTML = `
                <div style="text-align: center; padding: 40px; color: #f44336;">
                    <h3>Erro ao iniciar simulação</h3>
                    <p>${result.error}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro:', error);
        document.getElementById('simulation-results').innerHTML = `
            <div style="text-align: center; padding: 40px; color: #f44336;">
                <h3>Erro ao executar simulação</h3>
                <p>Verifique o console do navegador (F12) para mais detalhes.</p>
                <p style="font-size: 0.9em; color: #666;">Erro: ${error.message}</p>
            </div>
        `;
    }
}

// Polling para receber dados da simulação via MQTT
async function startSimulationPolling() {
    if (simulationInterval) {
        clearInterval(simulationInterval);
    }
    
    simulationInterval = setInterval(async () => {
        try {
            // Verifica status da simulação
            const statusResponse = await fetch('/api/simulation/status');
            const status = await statusResponse.json();
            
            // Atualiza progresso
            const progressElement = document.getElementById('simulation-progress');
            if (progressElement) {
                progressElement.textContent = status.progress.toFixed(0) + '%';
            }
            
            // Busca mensagens da simulação
            const messagesResponse = await fetch('/api/simulation/messages');
            const messagesResult = await messagesResponse.json();
            
            if (messagesResult.messages && messagesResult.messages.length > 0) {
                // Atualiza dados da simulação
                simulationData = messagesResult.messages.map(msg => msg.data);
                
                const pointsElement = document.getElementById('simulation-points');
                if (pointsElement) {
                    pointsElement.textContent = simulationData.length;
                }
            }
            
            // Se a simulação terminou
            if (!status.running && status.data && status.data.completed) {
                clearInterval(simulationInterval);
                simulationInterval = null;
                
                // Exibe resultados
                displaySimulationResults(status.data.results, status.data.metrics);
            } else if (!status.running && status.data && status.data.error) {
                clearInterval(simulationInterval);
                simulationInterval = null;
                
                document.getElementById('simulation-results').innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #f44336;">
                        <h3>Erro na simulação</h3>
                        <p>${status.data.error}</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Erro no polling:', error);
        }
    }, 1000); // Atualiza a cada 1 segundo
}

// Exibe resultados da simulação
function displaySimulationResults(results, metrics) {
    // Cria a estrutura HTML com os 4 gráficos
    document.getElementById('simulation-results').innerHTML = `
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-value" id="metric-rmse">${metrics.rmse.toFixed(3)}</div>
                <div class="metric-label">RMSE</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="metric-range">${metrics.percent_in_range.toFixed(1)}%</div>
                <div class="metric-label">% Tempo em Faixa</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="metric-violations">${metrics.violations}</div>
                <div class="metric-label">Violações</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="metric-energy">${metrics.energy_consumption.toFixed(0)}</div>
                <div class="metric-label">Energia Total</div>
            </div>
        </div>
        
        <div class="simulation-charts-grid">
            <div class="chart-box">
                <h3>Temperatura Atual vs Setpoint</h3>
                <div class="chart-container" style="height: 250px;">
                    <canvas id="tempComparisonChart"></canvas>
                </div>
            </div>
            
            <div class="chart-box">
                <h3>Potência de Refrigeração (PCRAC)</h3>
                <div class="chart-container" style="height: 250px;">
                    <canvas id="powerChart"></canvas>
                </div>
            </div>
            
            <div class="chart-box">
                <h3>Erro de Temperatura (T_atual - Setpoint)</h3>
                <div class="chart-container" style="height: 250px;">
                    <canvas id="errorChart"></canvas>
                </div>
            </div>
            
            <div class="chart-box">
                <h3>Temperatura de Saída ao Longo do Tempo</h3>
                <div class="chart-container" style="height: 250px;">
                    <canvas id="tempOutputChart"></canvas>
                </div>
            </div>
        </div>
    `;
    
    // Plota os 4 gráficos
    plotSimulationChart(results);
}
