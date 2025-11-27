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


def test_strategy_intervals(
    data: pd.DataFrame,
    strategy,
    params: Dict,
    interval_type: str = 'yearly',
    custom_days: Optional[int] = None,
    cash: float = 100,
    commission: float = 0.01
) -> Dict[str, Any]:
    """
    Prueba una estrategia con parámetros fijos en todo el dataset y por intervalos.
    
    Args:
        data: DataFrame con datos OHLCV
        strategy: Clase de estrategia
        params: Diccionario con parámetros de la estrategia
        interval_type: Tipo de intervalo ('yearly', 'quarterly', 'custom')
        custom_days: Número de días para intervalos personalizados
        cash: Capital inicial
        commission: Comisión por operación
        
    Returns:
        Diccionario con:
            - 'full': Estadísticas del backtest completo
            - 'intervals': Lista de tuplas (período, estadísticas)
    """
    results = {}
    
    # 1. Backtest completo
    print("\n   Ejecutando backtest completo...")
    bt_full = Backtest(data, strategy, cash=cash, commission=commission)
    stats_full = bt_full.run(**params)
    results['full'] = stats_full
    
    # 2. Dividir datos por intervalos
    intervals = _split_data_by_intervals(data, interval_type, custom_days)
    
    # 3. Ejecutar backtest en cada intervalo
    print(f"\n   Ejecutando backtests por intervalos ({interval_type})...")
    interval_results = []
    
    for i, (period_name, period_data) in enumerate(intervals, 1):
        if len(period_data) < 10:  # Saltar intervalos muy pequeños
            continue
            
        bt_interval = Backtest(period_data, strategy, cash=cash, commission=commission)
        try:
            stats_interval = bt_interval.run(**params)
            interval_results.append((period_name, stats_interval))
            print(f"      [{i}/{len(intervals)}] {period_name}: Return {stats_interval['Return [%]']:.2f}%")
        except Exception as e:
            print(f"      [{i}/{len(intervals)}] {period_name}: Error - {str(e)}")
            continue
    
    results['intervals'] = interval_results
    
    return results


def _split_data_by_intervals(
    data: pd.DataFrame,
    interval_type: str,
    custom_days: Optional[int] = None
) -> List[tuple]:
    """
    Divide los datos en intervalos de tiempo.
    
    Args:
        data: DataFrame con datos OHLCV
        interval_type: 'yearly', 'quarterly', 'custom'
        custom_days: Días para intervalos personalizados
        
    Returns:
        Lista de tuplas (nombre_período, datos_período)
    """
    intervals = []
    
    if interval_type == 'yearly':
        # Agrupar por año
        for year in data.index.year.unique():
            year_data = data[data.index.year == year]
            if len(year_data) > 0:
                intervals.append((f"Año {year}", year_data))
                
    elif interval_type == 'quarterly':
        # Agrupar por trimestre
        for year in data.index.year.unique():
            for quarter in range(1, 5):
                quarter_data = data[
                    (data.index.year == year) & 
                    (data.index.quarter == quarter)
                ]
                if len(quarter_data) > 0:
                    intervals.append((f"{year} Q{quarter}", quarter_data))
                    
    elif interval_type == 'custom' and custom_days:
        # Dividir por número de días personalizado
        start_idx = 0
        interval_num = 1
        
        while start_idx < len(data):
            end_idx = min(start_idx + custom_days, len(data))
            interval_data = data.iloc[start_idx:end_idx]
            
            if len(interval_data) > 0:
                start_date = interval_data.index[0].strftime('%Y-%m-%d')
                end_date = interval_data.index[-1].strftime('%Y-%m-%d')
                intervals.append((f"Período {interval_num} ({start_date} a {end_date})", interval_data))
                
            start_idx = end_idx
            interval_num += 1
    else:
        raise ValueError(f"Tipo de intervalo no válido: {interval_type}")
    
    return intervals
