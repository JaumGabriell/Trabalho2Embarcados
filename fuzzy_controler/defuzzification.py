import numpy as np

class Defuzzification:
    """Métodos de defuzzificação"""
    
    def centroid(self, output_aggregation, mf):
        """Defuzzificação por centroide (centro de área)"""
        universe = mf.potencia_crac_universe
        aggregated_mf = np.zeros_like(universe)
        
        for term, activation in output_aggregation.items():
            if activation > 0:
                term_mf = mf.potencia_crac_mf[term](universe)
                aggregated_mf = np.maximum(aggregated_mf, np.minimum(term_mf, activation))
        
        if np.sum(aggregated_mf) == 0:
            return 50.0
        
        centroid = np.sum(universe * aggregated_mf) / np.sum(aggregated_mf)
        return float(centroid)
