"""
Módulo de Testing Multimercado

Este módulo proporciona funciones para probar estrategias en múltiples
símbolos y períodos de tiempo, y analizar resultados comparativos.
"""

# Imports necesarios
from backtesting import Backtest
from backtesting.lib import MultiBacktest
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union


def compare_market_results(
    stats_list: Union[pd.DataFrame, List[pd.Series]],
    market_names: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Compara resultados de backtesting entre diferentes mercados.
    
    Args:
        stats_list: DataFrame de MultiBacktest o lista de Series de stats
        market_names: Nombres personalizados para los mercados (opcional)
    
    Returns:
        DataFrame con métricas comparativas entre mercados
    
    Example:
        >>> stats = btm.run()  # MultiBacktest
        >>> comparison = compare_market_results(stats, 
        ...     market_names=['BTC', 'ETH', 'BNB'])
    """
    # Convertir a DataFrame si es necesario
    if isinstance(stats_list, list):
        stats_df = pd.DataFrame(stats_list).T
    else:
        stats_df = stats_list
    
    # Asignar nombres si se proporcionan
    if market_names:
        stats_df.columns = market_names[:len(stats_df.columns)]
    
    # Seleccionar métricas clave para comparación
    key_metrics = [
        'Return [%]',
        'Buy & Hold Return [%]',
        'Sharpe Ratio',
        'Max. Drawdown [%]',
        'Win Rate [%]',
        '# Trades',
        'CAGR [%]',
        'Sortino Ratio'
    ]
    
    # Filtrar solo métricas disponibles
    available_metrics = [m for m in key_metrics if m in stats_df.index]
    comparison_df = stats_df.loc[available_metrics]
    
    return comparison_df


def generate_market_summary(
    stats_df: pd.DataFrame,
    market_categories: Optional[Dict[str, List[int]]] = None
) -> pd.DataFrame:
    """
    Genera resumen estadístico por categoría de mercado.
    
    Args:
        stats_df: DataFrame con resultados de MultiBacktest
        market_categories: Diccionario con categorías y sus índices
                          Ej: {'Cripto': [0,1,2], 'Indices': [5]}
    
    Returns:
        DataFrame con estadísticas agregadas por categoría
    
    Example:
        >>> categories = {
        ...     'Cripto': [0, 1, 2, 3, 4],
        ...     'Indices': [5],
        ...     'Forex': [6],
        ...     'Commodities': [7]
        ... }
        >>> summary = generate_market_summary(stats, categories)
    """
    if market_categories is None:
        # Asumir todo es una categoría
        market_categories = {'All Markets': list(range(len(stats_df.columns)))}
    
    summary_data = {}
    
    for category, indices in market_categories.items():
        # Seleccionar columnas de la categoría
        category_stats = stats_df.iloc[:, indices]
        
        # Calcular estadísticas
        summary_data[category] = {
            'Avg Return [%]': category_stats.loc['Return [%]'].mean(),
            'Best Return [%]': category_stats.loc['Return [%]'].max(),
            'Worst Return [%]': category_stats.loc['Return [%]'].min(),
            'Avg Sharpe': category_stats.loc['Sharpe Ratio'].mean(),
            'Avg Win Rate [%]': category_stats.loc['Win Rate [%]'].mean(),
            'Total Trades': category_stats.loc['# Trades'].sum(),
            'Markets': len(indices)
        }
    
    summary_df = pd.DataFrame(summary_data).T
    return summary_df


def rank_markets_by_metric(
    stats_df: pd.DataFrame,
    metric: str = 'Return [%]',
    ascending: bool = False,
    market_names: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Rankea mercados por una métrica específica.
    
    Args:
        stats_df: DataFrame con resultados de MultiBacktest
        metric: Métrica para rankear (ej: 'Return [%]', 'Sharpe Ratio')
        ascending: Si True, ordena de menor a mayor
        market_names: Nombres personalizados para los mercados
    
    Returns:
        DataFrame con ranking de mercados
    
    Example:
        >>> # Mejores mercados por retorno
        >>> ranking = rank_markets_by_metric(stats, 'Return [%]')
        >>> 
        >>> # Mercados con menor drawdown
        >>> ranking = rank_markets_by_metric(stats, 
        ...     'Max. Drawdown [%]', ascending=True)
    """
    if metric not in stats_df.index:
        raise ValueError(f"Métrica '{metric}' no encontrada en resultados")
    
    # Extraer valores de la métrica
    metric_values = stats_df.loc[metric].copy()
    
    # Asignar nombres si se proporcionan
    if market_names:
        metric_values.index = market_names[:len(metric_values)]
    
    # Ordenar
    ranked = metric_values.sort_values(ascending=ascending)
    
    # Crear DataFrame con ranking
    ranking_df = pd.DataFrame({
        'Rank': range(1, len(ranked) + 1),
        'Market': ranked.index,
        metric: ranked.values
    })
    
    ranking_df.set_index('Rank', inplace=True)
    
    return ranking_df


def calculate_consistency_score(
    stats_df: pd.DataFrame,
    metrics: Optional[List[str]] = None
) -> pd.Series:
    """
    Calcula un score de consistencia para cada mercado.
    
    El score considera múltiples métricas y penaliza alta volatilidad
    y drawdowns excesivos.
    
    Args:
        stats_df: DataFrame con resultados de MultiBacktest
        metrics: Lista de métricas a considerar (opcional)
    
    Returns:
        Series con scores de consistencia por mercado
    
    Example:
        >>> scores = calculate_consistency_score(stats)
        >>> best_market = scores.idxmax()
    """
    if metrics is None:
        metrics = ['Return [%]', 'Sharpe Ratio', 'Win Rate [%]']
    
    # Normalizar métricas (0-1)
    normalized_scores = pd.DataFrame()
    
    for metric in metrics:
        if metric in stats_df.index:
            values = stats_df.loc[metric]
            # Normalizar a rango 0-1
            min_val = values.min()
            max_val = values.max()
            if max_val != min_val:
                normalized = (values - min_val) / (max_val - min_val)
            else:
                normalized = pd.Series([0.5] * len(values), index=values.index)
            normalized_scores[metric] = normalized
    
    # Penalizar por drawdown (invertir porque menor es mejor)
    if 'Max. Drawdown [%]' in stats_df.index:
        dd_values = stats_df.loc['Max. Drawdown [%]'].abs()
        min_dd = dd_values.min()
        max_dd = dd_values.max()
        if max_dd != min_dd:
            dd_penalty = 1 - (dd_values - min_dd) / (max_dd - min_dd)
        else:
            dd_penalty = pd.Series([0.5] * len(dd_values), index=dd_values.index)
        normalized_scores['DD_Score'] = dd_penalty
    
    # Calcular score promedio
    consistency_score = normalized_scores.mean(axis=1)
    
    return consistency_score


def get_best_worst_markets(
    stats_df: pd.DataFrame,
    metric: str = 'Return [%]',
    n: int = 3,
    market_names: Optional[List[str]] = None
) -> Dict[str, List[str]]:
    """
    Identifica los mejores y peores mercados según una métrica.
    
    Args:
        stats_df: DataFrame con resultados de MultiBacktest
        metric: Métrica para evaluar
        n: Número de mercados a retornar en cada categoría
        market_names: Nombres personalizados para los mercados
    
    Returns:
        Diccionario con listas de 'best' y 'worst' mercados
    
    Example:
        >>> bw = get_best_worst_markets(stats, 'Sharpe Ratio', n=3)
        >>> print(f"Mejores: {bw['best']}")
        >>> print(f"Peores: {bw['worst']}")
    """
    ranking = rank_markets_by_metric(stats_df, metric, market_names=market_names)
    
    best_markets = ranking.head(n)['Market'].tolist()
    worst_markets = ranking.tail(n)['Market'].tolist()[::-1]  # Invertir orden
    
    return {
        'best': best_markets,
        'worst': worst_markets
    }
