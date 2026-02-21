"""
Módulo de optimización y walk-forward analysis.

Basado en el archivo optimize.py original, con mejoras en organización
y manejo de resultados.
"""

from backtesting import Backtest
import pandas as pd
from typing import Callable, Optional, Dict, List, Any

def walk_forward(data:pd.DataFrame,
                 strategy,cash,maximize:str = 'Sortino Ratio'):
    
    stats_master = []
    
    size_optimization = 1095
    size_test = int(size_optimization * 0.35)
    train = data.iloc[:size_optimization]
    test = data.iloc[size_optimization:size_optimization+size_test]
    df = data.iloc[size_optimization+size_test:]
    brocks = [df.iloc[i:i+size_test] for i in range(size_optimization,len(data),size_test) if i < len(df)]
    
    bt = Backtest(train,strategy=strategy,cash=cash)
    stats = optimize_auto(bt, strategy, maximize, constraint)
    
    bt = Backtest(test, strategy, cash=cash, commission=commission)
    stats = bt.run(**stats._strategy._params)
    stats_master.append(stats)
# Walk-forward loop
    for i,j in enumerate(brocks):
    
        bt = Backtest(i, strategy, cash=cash, commission=commission)
        stats = optimize_auto(bt, strategy, maximize, constraint)
        
        bt = Backtest(j+i, strategy, cash=cash, commission=commission)
        stats = bt.run(**stats._strategy._params)
        stats_master.append(stats)
    
    return stats_master

        
    

def _walk_forward(
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

if __name__== "__main__":
    from pathlib import Path
    import sys
# Obtener el directorio raíz del proyecto (3 niveles arriba de este archivo)
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    print(f"Project root set to: {project_root}")
    import yfinance as yf
    from strategies.sma_strategies import BTSMAStrategy
    df = yf.download("BTC-USD", period='max')
    #print(df)
    walk_forward(df,BTSMAStrategy,17)
    
