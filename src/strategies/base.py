"""
Clase base abstracta para todas las estrategias de trading.

Proporciona una interfaz común y métodos helper para todas las estrategias.
"""

from backtesting import Strategy
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseStrategy(Strategy, ABC):
    """
    Clase base para todas las estrategias.
    
    Todas las estrategias deben:
    1. Heredar de esta clase
    2. Definir el atributo opt_ranges como un diccionario
    3. Implementar los métodos init() y next()
    """
    
    # Este atributo debe ser sobrescrito en cada estrategia
    opt_ranges: Dict[str, Any] = {}
    
    @abstractmethod
    def init(self):
        """
        Inicializa indicadores y variables de la estrategia.
        Debe ser implementado por cada estrategia.
        """
        pass
    
    @abstractmethod
    def next(self):
        """
        Lógica de trading ejecutada en cada barra.
        Debe ser implementado por cada estrategia.
        """
        pass
    
    def get_params(self) -> Dict[str, Any]:
        """
        Retorna los parámetros actuales de la estrategia.
        
        Returns:
            Diccionario con los parámetros
        """
        params = {}
        for key in self.opt_ranges.keys():
            if hasattr(self, key):
                params[key] = getattr(self, key)
        return params
    
    def __repr__(self) -> str:
        """
        Representación en string de la estrategia.
        """
        params = self.get_params()
        params_str = ", ".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.__class__.__name__}({params_str})"
