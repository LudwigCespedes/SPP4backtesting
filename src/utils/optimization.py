"""
Módulo de optimización y walk-forward analysis.

Basado en el archivo optimize.py original, con mejoras en organización
y manejo de resultados.
"""

from backtesting import Backtest
import pandas as pd
from typing import Callable, Optional, Dict, List, Any


def walk_forward(
    data: pd.DataFrame,
    strategy,
    depp: int = 365,
    maximize: str = 'Sortino Ratio',
    cash: float = 100,
    commission: float = 0.01,
    constraint: Optional[Callable] = None
) -> List[Any]:
    """
    Ejecuta optimización walk-forward sobre los datos.
    
    Args:
        data: DataFrame con datos OHLCV
        strategy: Clase de estrategia a optimizar
        depp: Período de walk-forward en días
        maximize: Métrica a maximizar
        cash: Capital inicial
        commission: Comisión por operación
        constraint: Función de restricción para optimización
        
    Returns:
        Lista de estadísticas de cada período
    """
    train = data.iloc[:len(data)//4]
    test = data.iloc[len(data)//4:int((len(data)//2))]
    
    stats_master = []

    # Optimización inicial en train
    bt = Backtest(train, strategy, cash=cash, commission=commission)
    stats = optimize_auto(bt, strategy, maximize, constraint)
    
    # Evaluación inicial en test
    bt = Backtest(test, strategy, cash=cash, commission=commission)
    stats = bt.run(**stats._strategy._params)
    stats_master.append(stats)
    
    # Walk-forward loop
    for i in range(len(data)//2, len(data), depp):
        train = pd.concat([train[len(train)//2:], test])
        train = train[~train.index.duplicated(keep="first")].sort_index()

        test = pd.concat([test[len(test)//2:], data.iloc[i-depp:i+depp]])
        test = test[~test.index.duplicated(keep="first")].sort_index()

        bt = Backtest(train, strategy, cash=cash, commission=commission)
        stats = optimize_auto(bt, strategy, maximize, constraint)
        
        bt = Backtest(test, strategy, cash=cash, commission=commission)
        stats = bt.run(**stats._strategy._params)
        stats_master.append(stats)
    
    return stats_master


def optimize_auto(
    bt: Backtest,
    StrategyCls,
    maximize: str = 'Sortino Ratio',
    constraint: Optional[Callable] = None
):
    """
    Optimiza automáticamente una estrategia usando sus rangos definidos.
    
    Args:
        bt: Instancia de Backtest
        StrategyCls: Clase de estrategia con atributo opt_ranges
        maximize: Métrica a maximizar
        constraint: Función de restricción
        
    Returns:
        Estadísticas de la mejor configuración
        
    Raises:
        ValueError: Si la estrategia no tiene opt_ranges definido
    """
    ranges = getattr(StrategyCls, 'opt_ranges', None)
    if not ranges:
        raise ValueError(
            f"La estrategia {StrategyCls.__name__} debe definir 'opt_ranges' "
            "(diccionario de rangos de parámetros)."
        )
    
    return bt.optimize(**ranges, maximize=maximize, constraint=constraint)


def run_simple_backtest(
    data: pd.DataFrame,
    strategy,
    cash: float = 10,
    commission: float = 0.01,
    **strategy_params
) -> Any:
    """
    Ejecuta un backtest simple sin optimización.
    
    Args:
        data: DataFrame con datos OHLCV
        strategy: Clase de estrategia
        cash: Capital inicial
        commission: Comisión por operación
        **strategy_params: Parámetros de la estrategia
        
    Returns:
        Estadísticas del backtest
    """
    bt = Backtest(data, strategy, cash=cash, commission=commission)
    stats = bt.run(**strategy_params)
    return stats
