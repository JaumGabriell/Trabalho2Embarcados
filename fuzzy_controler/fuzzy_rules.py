class FuzzyRules:
    """
    Base de regras fuzzy CORRIGIDA para controle de refrigeração
    Tipo: Mamdani
    Estrutura: IF-THEN com 4 antecedentes e 1 consequente
    
    LÓGICA CORRIGIDA:
    erro = T_atual - T_setpoint (22°C)
    
    Termos linguísticos:
    - PB (Positivo Big): erro > +4°C → Temp MUITO ACIMA → CRAC em POTÊNCIA MÁXIMA (MA)
    - PM (Positivo Medium): erro +2 a +4°C → Temp ACIMA → CRAC em POTÊNCIA ALTA (A)
    - PS (Positivo Small): erro 0 a +2°C → Temp POUCO ACIMA → CRAC em POTÊNCIA MÉDIA/ALTA (M/A)
    - ZE (Zero): erro próximo de 0 → Temp NO SETPOINT → CRAC em POTÊNCIA MÉDIA (M)
    - NS (Negativo Small): erro 0 a -2°C → Temp POUCO ABAIXO → CRAC em POTÊNCIA BAIXA (B)
    - NM (Negativo Medium): erro -2 a -4°C → Temp ABAIXO → CRAC em POTÊNCIA MUITO BAIXA (MB)
    - NB (Negativo Big): erro < -4°C → Temp MUITO ABAIXO → CRAC MÍNIMO (MB)
    """
    
    def __init__(self):
        self.rules_base = self._create_rules_base()
    
    def _create_rules_base(self):
        """
        Cria a base de regras fuzzy completa e CORRETA
        Total: 7×7×3×3 = 441 regras (simplificadas para casos principais)
        """
        rules = []
        
        # ========================================================================
        # GRUPO 1: ERRO POSITIVO GRANDE (PB) - TEMPERATURA MUITO ALTA
        # Necessita REFRIGERAÇÃO MÁXIMA independente de outras variáveis
        # ========================================================================
        
        # Erro PB: sempre potência máxima ou alta
        for delta in ['NB', 'NM', 'NS', 'ZE', 'PS', 'PM', 'PB']:
            for temp_ext in ['Baixa', 'Media', 'Alta']:
                for carga in ['Baixa', 'Media', 'Alta']:
                    rules.append({
                        'erro': 'PB',
                        'delta_erro': delta,
                        'temp_externa': temp_ext,
                        'carga_termica': carga,
                        'potencia_crac': 'MA'  # Sempre potência máxima
                    })
        
        # ========================================================================
        # GRUPO 2: ERRO POSITIVO MÉDIO (PM) - TEMPERATURA ALTA
        # Necessita REFRIGERAÇÃO ALTA, modulada por outras variáveis
        # ========================================================================
        
        for delta in ['NB', 'NM', 'NS']:  # Erro aumentando ou estável
            for temp_ext in ['Baixa', 'Media']:
                for carga in ['Baixa', 'Media']:
                    rules.append({
                        'erro': 'PM',
                        'delta_erro': delta,
                        'temp_externa': temp_ext,
                        'carga_termica': carga,
                        'potencia_crac': 'A'  # Alta potência
                    })
        
        # PM + condições desfavoráveis → potência máxima
        for delta in ['NB', 'NM', 'NS', 'ZE', 'PS']:  # Aumentado para incluir PS
            rules.append({'erro': 'PM', 'delta_erro': delta, 'temp_externa': 'Alta', 'carga_termica': 'Alta', 'potencia_crac': 'MA'})
            rules.append({'erro': 'PM', 'delta_erro': delta, 'temp_externa': 'Alta', 'carga_termica': 'Media', 'potencia_crac': 'A'})
            rules.append({'erro': 'PM', 'delta_erro': delta, 'temp_externa': 'Media', 'carga_termica': 'Alta', 'potencia_crac': 'A'})
            rules.append({'erro': 'PM', 'delta_erro': delta, 'temp_externa': 'Media', 'carga_termica': 'Media', 'potencia_crac': 'A'})
        
        # PM + erro diminuindo (favorável) → potência alta
        for delta in ['PS', 'PM', 'PB']:  # Erro diminuindo
            for temp_ext in ['Baixa', 'Media', 'Alta']:
                for carga in ['Baixa', 'Media', 'Alta']:
                    rules.append({
                        'erro': 'PM',
                        'delta_erro': delta,
                        'temp_externa': temp_ext,
                        'carga_termica': carga,
                        'potencia_crac': 'A'  # Alta (não máxima pois está melhorando)
                    })
        
        # ========================================================================
        # GRUPO 3: ERRO POSITIVO PEQUENO (PS) - TEMPERATURA LEVEMENTE ALTA
        # Necessita REFRIGERAÇÃO MÉDIA/ALTA
        # ========================================================================
        
        # PS + erro aumentando → ação forte
        for delta in ['NB', 'NM', 'NS']:
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Baixa', 'carga_termica': 'Baixa', 'potencia_crac': 'M'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Baixa', 'carga_termica': 'Media', 'potencia_crac': 'A'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Baixa', 'carga_termica': 'Alta', 'potencia_crac': 'A'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Media', 'carga_termica': 'Baixa', 'potencia_crac': 'M'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Media', 'carga_termica': 'Media', 'potencia_crac': 'A'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Media', 'carga_termica': 'Alta', 'potencia_crac': 'A'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Alta', 'carga_termica': 'Baixa', 'potencia_crac': 'A'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Alta', 'carga_termica': 'Media', 'potencia_crac': 'A'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Alta', 'carga_termica': 'Alta', 'potencia_crac': 'MA'})
        
        # PS + erro estável ou diminuindo → ação moderada
        for delta in ['ZE', 'PS', 'PM', 'PB']:
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Baixa', 'carga_termica': 'Baixa', 'potencia_crac': 'B'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Baixa', 'carga_termica': 'Media', 'potencia_crac': 'M'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Baixa', 'carga_termica': 'Alta', 'potencia_crac': 'M'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Media', 'carga_termica': 'Baixa', 'potencia_crac': 'M'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Media', 'carga_termica': 'Media', 'potencia_crac': 'M'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Media', 'carga_termica': 'Alta', 'potencia_crac': 'A'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Alta', 'carga_termica': 'Baixa', 'potencia_crac': 'M'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Alta', 'carga_termica': 'Media', 'potencia_crac': 'A'})
            rules.append({'erro': 'PS', 'delta_erro': delta, 'temp_externa': 'Alta', 'carga_termica': 'Alta', 'potencia_crac': 'A'})
        
        # ========================================================================
        # GRUPO 4: ERRO ZERO (ZE) - TEMPERATURA NO SETPOINT
        # Potência BALANCEADA conforme condições externas
        # ========================================================================
        
        # ZE + condições favoráveis → potência baixa
        rules.append({'erro': 'ZE', 'delta_erro': 'ZE', 'temp_externa': 'Baixa', 'carga_termica': 'Baixa', 'potencia_crac': 'B'})
        rules.append({'erro': 'ZE', 'delta_erro': 'ZE', 'temp_externa': 'Baixa', 'carga_termica': 'Media', 'potencia_crac': 'B'})
        
        # ZE + condições médias → potência média
        rules.append({'erro': 'ZE', 'delta_erro': 'ZE', 'temp_externa': 'Baixa', 'carga_termica': 'Alta', 'potencia_crac': 'M'})
        rules.append({'erro': 'ZE', 'delta_erro': 'ZE', 'temp_externa': 'Media', 'carga_termica': 'Baixa', 'potencia_crac': 'M'})
        rules.append({'erro': 'ZE', 'delta_erro': 'ZE', 'temp_externa': 'Media', 'carga_termica': 'Media', 'potencia_crac': 'M'})
        
        # ZE + condições desfavoráveis → potência alta
        rules.append({'erro': 'ZE', 'delta_erro': 'ZE', 'temp_externa': 'Media', 'carga_termica': 'Alta', 'potencia_crac': 'A'})
        rules.append({'erro': 'ZE', 'delta_erro': 'ZE', 'temp_externa': 'Alta', 'carga_termica': 'Baixa', 'potencia_crac': 'M'})
        rules.append({'erro': 'ZE', 'delta_erro': 'ZE', 'temp_externa': 'Alta', 'carga_termica': 'Media', 'potencia_crac': 'A'})
        rules.append({'erro': 'ZE', 'delta_erro': 'ZE', 'temp_externa': 'Alta', 'carga_termica': 'Alta', 'potencia_crac': 'A'})
        
        # ZE + erro aumentando (piorando) → ação preventiva
        for delta in ['NB', 'NM', 'NS']:
            for temp_ext in ['Baixa', 'Media', 'Alta']:
                for carga in ['Baixa', 'Media', 'Alta']:
                    pot = 'M' if temp_ext == 'Baixa' and carga == 'Baixa' else 'A'
                    rules.append({
                        'erro': 'ZE',
                        'delta_erro': delta,
                        'temp_externa': temp_ext,
                        'carga_termica': carga,
                        'potencia_crac': pot
                    })
        
        # ZE + erro diminuindo (melhorando) → reduzir potência
        for delta in ['PS', 'PM', 'PB']:
            for temp_ext in ['Baixa', 'Media', 'Alta']:
                for carga in ['Baixa', 'Media', 'Alta']:
                    pot = 'MB' if temp_ext == 'Baixa' and carga == 'Baixa' else 'B'
                    rules.append({
                        'erro': 'ZE',
                        'delta_erro': delta,
                        'temp_externa': temp_ext,
                        'carga_termica': carga,
                        'potencia_crac': pot
                    })
        
        # ========================================================================
        # GRUPO 5: ERRO NEGATIVO PEQUENO (NS) - TEMPERATURA LEVEMENTE BAIXA
        # Reduzir REFRIGERAÇÃO (potência baixa)
        # ========================================================================
        
        for delta in ['NB', 'NM', 'NS', 'ZE']:
            for temp_ext in ['Baixa', 'Media', 'Alta']:
                for carga in ['Baixa', 'Media', 'Alta']:
                    # Temp abaixo do setpoint → reduzir CRAC
                    if temp_ext == 'Alta' and carga == 'Alta':
                        pot = 'M'  # Condições ruins, manter alguma potência
                    else:
                        pot = 'B' if carga != 'Baixa' else 'MB'
                    
                    rules.append({
                        'erro': 'NS',
                        'delta_erro': delta,
                        'temp_externa': temp_ext,
                        'carga_termica': carga,
                        'potencia_crac': pot
                    })
        
        # NS + erro piorando (ficando mais negativo) → reduzir ainda mais
        for delta in ['PS', 'PM', 'PB']:
            for temp_ext in ['Baixa', 'Media', 'Alta']:
                for carga in ['Baixa', 'Media', 'Alta']:
                    rules.append({
                        'erro': 'NS',
                        'delta_erro': delta,
                        'temp_externa': temp_ext,
                        'carga_termica': carga,
                        'potencia_crac': 'MB'
                    })
        
        # ========================================================================
        # GRUPO 6: ERRO NEGATIVO MÉDIO (NM) - TEMPERATURA BAIXA
        # MÍNIMA REFRIGERAÇÃO
        # ========================================================================
        
        for delta in ['NB', 'NM', 'NS', 'ZE', 'PS', 'PM', 'PB']:
            for temp_ext in ['Baixa', 'Media', 'Alta']:
                for carga in ['Baixa', 'Media', 'Alta']:
                    # Temperatura muito abaixo → CRAC mínimo
                    rules.append({
                        'erro': 'NM',
                        'delta_erro': delta,
                        'temp_externa': temp_ext,
                        'carga_termica': carga,
                        'potencia_crac': 'MB'
                    })
        
        # ========================================================================
        # GRUPO 7: ERRO NEGATIVO GRANDE (NB) - TEMPERATURA MUITO BAIXA
        # DESLIGAR REFRIGERAÇÃO (potência mínima absoluta)
        # ========================================================================
        
        for delta in ['NB', 'NM', 'NS', 'ZE', 'PS', 'PM', 'PB']:
            for temp_ext in ['Baixa', 'Media', 'Alta']:
                for carga in ['Baixa', 'Media', 'Alta']:
                    rules.append({
                        'erro': 'NB',
                        'delta_erro': delta,
                        'temp_externa': temp_ext,
                        'carga_termica': carga,
                        'potencia_crac': 'MB'  # Sempre potência mínima
                    })
        
        return rules
    
    def get_applicable_rules(self, erro_memberships, delta_erro_memberships, 
                            temp_externa_memberships, carga_termica_memberships):
        """
        Retorna regras aplicáveis com seus graus de ativação
        """
        applicable_rules = []
        
        for rule in self.rules_base:
            # Calcula grau de ativação da regra (mínimo dos antecedentes)
            activation = min(
                erro_memberships.get(rule['erro'], 0),
                delta_erro_memberships.get(rule['delta_erro'], 0),
                temp_externa_memberships.get(rule['temp_externa'], 0),
                carga_termica_memberships.get(rule['carga_termica'], 0)
            )
            
            if activation > 0:
                applicable_rules.append({
                    'rule': rule,
                    'activation': activation
                })
        
        return applicable_rules
