# Sistema Fuzzy para Controle de Refrigeração de Data Center

Sistema de controle inteligente baseado em lógica fuzzy para gerenciamento de temperatura em centros de dados.

##  Instalação

### 1. Ativar o ambiente virtual
```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

## ▶ Executar o Sistema

```bash
python app.py
```

Acesse: **http://localhost:5500**

##  Funcionalidades

-  Controle Fuzzy MISO (4 entradas, 1 saída)
-  Motor de Inferência Mamdani
-  Simulação de 24 horas
-  Interface web interativa
-  Sistema MQTT para monitoramento
-  Visualização de funções de pertinência
-  Gráficos em tempo real

##  Variáveis do Sistema

### Entradas:
- Erro de Temperatura (e)
- Variação do Erro (Δe)
- Temperatura Externa (Text)
- Carga Térmica (Qest)

### Saída:
- Potência CRAC (0-100%)

##  Configuração MQTT

Broker: broker.hivemq.com:1883
Tópicos:
- datacenter/fuzzy/alert
- datacenter/fuzzy/control
- datacenter/fuzzy/temp

##  Modelo Físico

```
T[n+1] = 0.9×T[n] - 0.08×PCRAC + 0.05×Qest + 0.02×Text + 3.5
```

##  Autores
João Gabriel de Carvalho Barbosa
Guilherme Oliveira e Brito

Projeto Final - Embarcados
Disciplina: C213