import numpy as np
from .membership_functions import MembershipFunctions
from .fuzzy_rules import FuzzyRules
from .defuzzification import Defuzzification

class FuzzyController:
    """
    Controlador Fuzzy MISO (Multiple Input, Single Output)
    Tipo: Mamdani com defuzzificação por centroide
    """
    
    def __init__(self):
        self.mf = MembershipFunctions()
        self.rules = FuzzyRules()
        self.defuzz = Defuzzification()
        self.last_inference = None
        
    def fuzzification(self, erro, delta_erro, temp_externa, carga_termica):
        """
        Converte valores crisp em graus de pertinência
        """
        fuzzy_inputs = {
            'erro': {},
            'delta_erro': {},
            'temp_externa': {},
            'carga_termica': {}
        }
        
        # Fuzzifica erro
        for term in self.mf.erro_terms:
            fuzzy_inputs['erro'][term] = self.mf.get_membership(
                'erro', term, erro
            )
        
        # Fuzzifica delta_erro
        for term in self.mf.delta_erro_terms:
            fuzzy_inputs['delta_erro'][term] = self.mf.get_membership(
                'delta_erro', term, delta_erro
            )
        
        # Fuzzifica temperatura externa
        for term in self.mf.temp_externa_terms:
            fuzzy_inputs['temp_externa'][term] = self.mf.get_membership(
                'temp_externa', term, temp_externa
            )
        
        # Fuzzifica carga térmica
        for term in self.mf.carga_termica_terms:
            fuzzy_inputs['carga_termica'][term] = self.mf.get_membership(
                'carga_termica', term, carga_termica
            )
        
        return fuzzy_inputs
    
    def inference(self, fuzzy_inputs):
        """
        Aplica as regras fuzzy e agrega os resultados
        Método: Mamdani (min-max)
        """
        activated_rules = []
        output_aggregation = {}
        
        # Inicializa agregação para cada termo de saída
        for term in self.mf.potencia_crac_terms:
            output_aggregation[term] = 0.0
        
        # Aplica cada regra
        for rule in self.rules.rules_base:
            # Calcula força de ativação da regra (AND = min)
            activation = min(
                fuzzy_inputs['erro'][rule['erro']],
                fuzzy_inputs['delta_erro'][rule['delta_erro']],
                fuzzy_inputs['temp_externa'][rule['temp_externa']],
                fuzzy_inputs['carga_termica'][rule['carga_termica']]
            )
            
            if activation > 0:
                activated_rules.append({
                    'rule': rule,
                    'activation': activation
                })
                
                # Agrega usando máximo (OR)
                output_term = rule['potencia_crac']
                output_aggregation[output_term] = max(
                    output_aggregation[output_term],
                    activation
                )
        
        return activated_rules, output_aggregation
    
    def calculate(self, erro, delta_erro, temp_externa, carga_termica):
        """
        Calcula a saída crisp do controlador fuzzy
        """
        # SATURAÇÃO: Limita valores extremos aos ranges das funções de pertinência
        # Isso garante que valores muito altos/baixos sejam tratados como os extremos válidos
        erro = np.clip(erro, -10, 10)              # Erro: -10 a +10°C
        delta_erro = np.clip(delta_erro, -5, 5)    # Delta: -5 a +5
        temp_externa = np.clip(temp_externa, 10, 35)  # Temp Externa: 10 a 35°C
        carga_termica = np.clip(carga_termica, 0, 100)  # Carga: 0 a 100%
        
        # 1. Fuzzificação
        fuzzy_inputs = self.fuzzification(
            erro, delta_erro, temp_externa, carga_termica
        )
        
        # 2. Inferência
        activated_rules, output_aggregation = self.inference(fuzzy_inputs)
        
        # 3. Defuzzificação (centroide)
        potencia_crac = self.defuzz.centroid(
            output_aggregation, 
            self.mf
        )
        
        # Limita saída entre 0 e 100
        potencia_crac = np.clip(potencia_crac, 0, 100)
        
        # Salva detalhes da última inferência
        self.last_inference = {
            'inputs': {
                'erro': erro,
                'delta_erro': delta_erro,
                'temp_externa': temp_externa,
                'carga_termica': carga_termica
            },
            'fuzzy_inputs': fuzzy_inputs,
            'activated_rules': activated_rules,
            'output_aggregation': output_aggregation,
            'potencia_crac': potencia_crac
        }
        
        return potencia_crac
    
    def get_inference_details(self):
        """Retorna detalhes da última inferência"""
        if self.last_inference is None:
            return None
        
        return {
            'inputs': self.last_inference['inputs'],
            'fuzzy_values': self.last_inference['fuzzy_inputs'],
            'activated_rules_count': len(self.last_inference['activated_rules']),
            'activated_rules': [
                {
                    'rule_id': i,
                    'activation': r['activation'],
                    'conditions': {
                        'erro': r['rule']['erro'],
                        'delta_erro': r['rule']['delta_erro'],
                        'temp_externa': r['rule']['temp_externa'],
                        'carga_termica': r['rule']['carga_termica']
                    },
                    'output': r['rule']['potencia_crac']
                }
                for i, r in enumerate(self.last_inference['activated_rules'][:10])  # Top 10
            ],
            'output': self.last_inference['potencia_crac']
        }
    
    def get_membership_functions_data(self):
        """Retorna dados das funções de pertinência para visualização"""
        return self.mf.get_all_membership_data()
    
    def get_rules_base(self):
        """Retorna a base de regras completa"""
        return {
            'total_rules': len(self.rules.rules_base),
            'rules': self.rules.rules_base[:50]  # Primeiras 50 regras
        }