import numpy as np

class PhysicalModel:
    """Modelo físico do data center"""
    
    def __init__(self):
        self.a = 0.9   # Inércia térmica
        self.b = -0.08 # Ganho CRAC
        self.c = 0.05  # Impacto carga térmica
        self.d = 0.02  # Influência temp externa
        self.e = 3.5   # Offset base
    
    def update_temperature(self, T_current, P_crac, Q_est, T_ext):
        """
        Função de transferência do sistema:
        T[n+1] = 0.9*T[n] - 0.08*PCRAC + 0.05*Qest + 0.02*Text + 3.5
        """
        T_next = (self.a * T_current + 
                  self.b * P_crac + 
                  self.c * Q_est + 
                  self.d * T_ext + 
                  self.e)
        return T_next
