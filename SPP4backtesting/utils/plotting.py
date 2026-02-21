"""
Módulo de visualización y guardado de resultados.

Basado en el archivo optimize.py original, con mejoras en organización
de archivos de salida.
"""

import pandas as pd
import matplotlib.pyplot as plt
import time
import os
from typing import List, Any, Optional
from datetime import datetime


def plot_stats(
    stats: List[Any],
    params_to_plot: Optional[List[str]] = None,
    save_dir: str = "results",
    strategy_name: str = "strategy"
) -> None:
    """
    Grafica y guarda estadísticas de backtesting.
    
    Args:
        stats: Lista de estadísticas de backtesting
        params_to_plot: Lista de métricas a graficar
        save_dir: Directorio donde guardar resultados
        strategy_name: Nombre de la estrategia para el archivo
    """
    if params_to_plot is None:
        params_to_plot = ['Alpha [%]', 'Win Rate [%]', 'Kelly Criterion', 'Sortino Ratio']
    
    stats_df = pd.DataFrame(stats)
    
    # Crear gráficos
    stats_df.loc[:, params_to_plot].plot(
        kind="bar",
        subplots=True,
        figsize=(10, 10),
        grid=True
    )
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Crear directorios si no existen
    csv_dir = os.path.join(save_dir, "csv")
    plots_dir = os.path.join(save_dir, "plots")
    xlsx_dir = os.path.join(save_dir, "xlsx")
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(xlsx_dir, exist_ok=True)
    
    # Guardar CSV y PNG con nombres descriptivos
    csv_path = os.path.join(csv_dir, f"{strategy_name}_{timestamp}.csv")
    png_path = os.path.join(plots_dir, f"{strategy_name}_{timestamp}.png")
    xlsx_path = os.path.join(xlsx_dir, f"{strategy_name}_{timestamp}.xlsx")
    
    stats_df.to_csv(csv_path)
    
    # Convertir columnas datetime con timezone a timezone-naive para Excel
    stats_df_excel = stats_df.copy()
    for col in stats_df_excel.columns:
        if pd.api.types.is_datetime64tz_dtype(stats_df_excel[col]):
            stats_df_excel[col] = stats_df_excel[col].dt.tz_localize(None)
    
    stats_df_excel.to_excel(xlsx_path)
    
    plt.savefig(png_path)
    plt.show()
    
    print(f"\nResultados guardados:")
    print(f"  CSV: {csv_path}")
    print(f"  PNG: {png_path}")
    print(f"  XLSX: {xlsx_path}")


def save_results(
    stats: Any,
    strategy_name: str,
    save_dir: str = "results",
    save_html: bool = True,
    save_csv: bool = True,
    save_xlsx: bool = True
) -> None:
    """
    Guarda resultados de un backtest individual.
    
    Args:
        stats: Estadísticas del backtest
        strategy_name: Nombre de la estrategia
        save_dir: Directorio donde guardar
        save_html: Si True, guarda reporte HTML
        save_csv: Si True, guarda estadísticas en CSV
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if save_csv:
        csv_dir = os.path.join(save_dir, "csv")
        os.makedirs(csv_dir, exist_ok=True)
        
        csv_path = os.path.join(csv_dir, f"{strategy_name}_{timestamp}.csv")
        stats_df = pd.Series(stats).to_frame(name='Value')
        stats_df.to_csv(csv_path)
        print(f"Estadísticas guardadas en: {csv_path}")
    
    if save_html:
        html_dir = os.path.join(save_dir, "html")
        os.makedirs(html_dir, exist_ok=True)
        
        # Nota: El método plot() de backtesting genera el HTML
        # pero necesita ser llamado desde el contexto del backtest
        print(f"Para guardar HTML, usa: bt.plot(filename='{html_dir}/{strategy_name}_{timestamp}.html')")


def print_summary(stats: Any) -> None:
    """
    Imprime un resumen de las estadísticas principales.
    
    Args:
        stats: Estadísticas del backtest
    """
    print("\n" + "="*60)
    print("RESUMEN DE BACKTEST")
    print("="*60)
    
    metrics = [
        'Start',
        'End',
        'Duration',
        'Return [%]',
        'Sharpe Ratio',
        'Sortino Ratio',
        'Max. Drawdown [%]',
        'Win Rate [%]',
        '# Trades',
    ]
    
    for metric in metrics:
        if hasattr(stats, metric.replace(' ', '_').replace('.', '').replace('[', '').replace(']', '').replace('%', 'Pct')):
            value = getattr(stats, metric.replace(' ', '_').replace('.', '').replace('[', '').replace(']', '').replace('%', 'Pct'))
            print(f"{metric:.<40} {value}")
    
    print("="*60 + "\n")


def plot_interval_comparison(
    interval_results: List[tuple],
    full_stats: Any,
    strategy_name: str,
    interval_type: str,
    save_dir: str = "results",
    params: dict = None
) -> None:
    """
    Crea gráficos comparativos de rendimiento por intervalos.
    
    Args:
        interval_results: Lista de tuplas (período, estadísticas)
        full_stats: Estadísticas del backtest completo
        strategy_name: Nombre de la estrategia
        interval_type: Tipo de intervalo usado
        save_dir: Directorio donde guardar
        params: Parámetros de la estrategia (opcional)
    """
    if not interval_results:
        print("No hay resultados de intervalos para graficar")
        return
    
    # Extraer datos para graficar
    periods = [period for period, _ in interval_results]
    returns = [stats['Return [%]'] for _, stats in interval_results]
    sharpe = [stats.get('Sharpe Ratio', 0) for _, stats in interval_results]
    sortino = [stats.get('Sortino Ratio', 0) for _, stats in interval_results]
    win_rate = [stats.get('Win Rate [%]', 0) for _, stats in interval_results]
    max_dd = [stats.get('Max. Drawdown [%]', 0) for _, stats in interval_results]
    
    # Crear string de parámetros para el título y nombre de archivo
    params_str = ""
    params_filename = ""
    if params:
        params_str = " | " + " ".join([f"{k}={v}" for k, v in params.items()])
        params_filename = "_" + "_".join([f"{k}{v}" for k, v in params.items()])
    
    # Crear figura con subplots
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle(f'{strategy_name} - Comparación por {interval_type}{params_str}', fontsize=16, fontweight='bold')
    
    # 1. Retorno %
    axes[0, 0].bar(range(len(periods)), returns, color='steelblue', alpha=0.7)
    axes[0, 0].axhline(y=full_stats['Return [%]'], color='red', linestyle='--', 
                       label=f'Completo: {full_stats["Return [%]"]:.2f}%')
    axes[0, 0].set_title('Retorno [%]')
    axes[0, 0].set_ylabel('Retorno %')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_xticks(range(len(periods)))
    axes[0, 0].set_xticklabels(periods, rotation=45, ha='right', fontsize=8)
    
    # 2. Sharpe Ratio
    axes[0, 1].bar(range(len(periods)), sharpe, color='green', alpha=0.7)
    axes[0, 1].axhline(y=full_stats.get('Sharpe Ratio', 0), color='red', linestyle='--',
                       label=f'Completo: {full_stats.get("Sharpe Ratio", 0):.2f}')
    axes[0, 1].set_title('Sharpe Ratio')
    axes[0, 1].set_ylabel('Sharpe Ratio')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_xticks(range(len(periods)))
    axes[0, 1].set_xticklabels(periods, rotation=45, ha='right', fontsize=8)
    
    # 3. Sortino Ratio
    axes[1, 0].bar(range(len(periods)), sortino, color='purple', alpha=0.7)
    axes[1, 0].axhline(y=full_stats.get('Sortino Ratio', 0), color='red', linestyle='--',
                       label=f'Completo: {full_stats.get("Sortino Ratio", 0):.2f}')
    axes[1, 0].set_title('Sortino Ratio')
    axes[1, 0].set_ylabel('Sortino Ratio')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_xticks(range(len(periods)))
    axes[1, 0].set_xticklabels(periods, rotation=45, ha='right', fontsize=8)
    
    # 4. Win Rate
    axes[1, 1].bar(range(len(periods)), win_rate, color='orange', alpha=0.7)
    axes[1, 1].axhline(y=full_stats.get('Win Rate [%]', 0), color='red', linestyle='--',
                       label=f'Completo: {full_stats.get("Win Rate [%]", 0):.2f}%')
    axes[1, 1].set_title('Win Rate [%]')
    axes[1, 1].set_ylabel('Win Rate %')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_xticks(range(len(periods)))
    axes[1, 1].set_xticklabels(periods, rotation=45, ha='right', fontsize=8)
    
    # 5. Max Drawdown
    axes[2, 0].bar(range(len(periods)), max_dd, color='red', alpha=0.7)
    axes[2, 0].axhline(y=full_stats.get('Max. Drawdown [%]', 0), color='darkred', linestyle='--',
                       label=f'Completo: {full_stats.get("Max. Drawdown [%]", 0):.2f}%')
    axes[2, 0].set_title('Max Drawdown [%]')
    axes[2, 0].set_ylabel('Max DD %')
    axes[2, 0].legend()
    axes[2, 0].grid(True, alpha=0.3)
    axes[2, 0].set_xticks(range(len(periods)))
    axes[2, 0].set_xticklabels(periods, rotation=45, ha='right', fontsize=8)
    
    # 6. Número de operaciones
    num_trades = [stats.get('# Trades', 0) for _, stats in interval_results]
    axes[2, 1].bar(range(len(periods)), num_trades, color='teal', alpha=0.7)
    axes[2, 1].axhline(y=full_stats.get('# Trades', 0), color='red', linestyle='--',
                       label=f'Completo: {full_stats.get("# Trades", 0)}')
    axes[2, 1].set_title('Número de Operaciones')
    axes[2, 1].set_ylabel('# Trades')
    axes[2, 1].legend()
    axes[2, 1].grid(True, alpha=0.3)
    axes[2, 1].set_xticks(range(len(periods)))
    axes[2, 1].set_xticklabels(periods, rotation=45, ha='right', fontsize=8)
    
    plt.tight_layout()
    
    # Guardar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plots_dir = os.path.join(save_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    png_path = os.path.join(plots_dir, f"{strategy_name}_intervals_{interval_type}{params_filename}_{timestamp}.png")
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    print(f"\n   Gráfico guardado: {png_path}")
    plt.show()


def save_interval_results(
    interval_results: List[tuple],
    full_stats: Any,
    strategy_name: str,
    interval_type: str,
    params: dict,
    save_dir: str = "results"
) -> None:
    """
    Guarda resultados de intervalos en CSV.
    
    Args:
        interval_results: Lista de tuplas (período, estadísticas)
        full_stats: Estadísticas del backtest completo
        strategy_name: Nombre de la estrategia
        interval_type: Tipo de intervalo
        params: Parámetros usados
        save_dir: Directorio donde guardar
    """
    # Crear DataFrame con resultados
    data = []
    
    # Agregar resultado completo
    data.append({
        'Período': 'COMPLETO',
        'Return [%]': full_stats['Return [%]'],
        'Sharpe Ratio': full_stats.get('Sharpe Ratio', 0),
        'Sortino Ratio': full_stats.get('Sortino Ratio', 0),
        'Max. Drawdown [%]': full_stats.get('Max. Drawdown [%]', 0),
        'Win Rate [%]': full_stats.get('Win Rate [%]', 0),
        '# Trades': full_stats.get('# Trades', 0),
        'Avg. Trade [%]': full_stats.get('Avg. Trade [%]', 0),
    })
    
    # Agregar resultados por intervalo
    for period, stats in interval_results:
        data.append({
            'Período': period,
            'Return [%]': stats['Return [%]'],
            'Sharpe Ratio': stats.get('Sharpe Ratio', 0),
            'Sortino Ratio': stats.get('Sortino Ratio', 0),
            'Max. Drawdown [%]': stats.get('Max. Drawdown [%]', 0),
            'Win Rate [%]': stats.get('Win Rate [%]', 0),
            '# Trades': stats.get('# Trades', 0),
            'Avg. Trade [%]': stats.get('Avg. Trade [%]', 0),
        })
    
    df = pd.DataFrame(data)
    
    # Crear string de parámetros para el nombre de archivo
    params_filename = "_" + "_".join([f"{k}{v}" for k, v in params.items()])
    
    # Guardar CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_dir = os.path.join(save_dir, "csv")
    os.makedirs(csv_dir, exist_ok=True)
    
    csv_path = os.path.join(csv_dir, f"{strategy_name}_intervals_{interval_type}{params_filename}_{timestamp}.csv")
    df.to_csv(csv_path, index=False)
    print(f"   Resultados guardados: {csv_path}")
    
    # Imprimir tabla resumen
    print("\n" + "="*100)
    print(f"RESUMEN DE RESULTADOS POR {interval_type.upper()}")
    print("="*100)
    print(df.to_string(index=False))
    print("="*100)
    
    # Imprimir parámetros usados
    print("\nParámetros utilizados:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    print()


def plot_multimarket_heatmaps(
    results_dict: dict,
    market_names: List[str],
    save_path: Optional[str] = None,
    figsize: tuple = (24, 12),
    cmap: str = "RdYlGn"
) -> tuple:
    """
    Genera mapas de calor individuales para cada mercado en un grid.
    
    Parameters:
    -----------
    results_dict : dict
        Diccionario con {idx: DataFrame} de resultados por mercado.
        Cada DataFrame debe tener parámetros n1 como filas y n2 como columnas.
    market_names : list
        Lista de nombres de los mercados (deben coincidir con las keys de results_dict)
    save_path : str, optional
        Ruta completa para guardar la figura (incluyendo extensión)
    figsize : tuple, optional
        Tamaño de la figura (ancho, alto). Default: (24, 12)
    cmap : str, optional
        Mapa de colores. Default: "RdYlGn" (rojo-amarillo-verde)
        
    Returns:
    --------
    fig, axes : matplotlib figure y axes
        Objetos de matplotlib para personalización adicional
        
    Example:
    --------
    >>> results = {0: df_btc, 1: df_eth, ...}
    >>> names = ['BTC', 'ETH', 'BNB', ...]
    >>> fig, axes = plot_multimarket_heatmaps(results, names, 'results/heatmaps.png')
    """
    import seaborn as sns
    
    num_markets = len(market_names)
    
    # Calcular grid óptimo (intentar 2 filas)
    ncols = 4
    nrows = (num_markets + ncols - 1) // ncols
    
    # Crear figura
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    fig.suptitle('Mapas de Calor de Retornos por Activo - Optimización SMA', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    # Aplanar axes para facilitar iteración
    if num_markets == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if nrows > 1 else [axes] if ncols == 1 else axes
    
    # Generar heatmap para cada mercado
    for idx, market_name in enumerate(market_names):
        ax = axes[idx]
        
        # Obtener datos del mercado
        market_data = results_dict[idx]
        
        # Crear heatmap
        sns.heatmap(
            market_data,
            annot=True,
            fmt=".2f",
            cmap=cmap,
            center=0,
            cbar=(idx == 0),  # Solo mostrar barra de color en el primer gráfico
            ax=ax,
            linewidths=0.5,
            linecolor='gray',
            vmin=-2,  # Valores mínimos y máximos para escala consistente
            vmax=3,
            annot_kws={"size": 8}
        )
        
        # Encontrar mejor combinación
        max_val = market_data.max().max()
        max_pos = market_data.stack().idxmax()
        
        # Título con información clave
        ax.set_title(
            f'{market_name}\n'
            f'Mejor: n1={max_pos[0]}, n2={max_pos[1]} (Return: {max_val:.2f}%)',
            fontsize=11,
            fontweight='bold',
            pad=10
        )
        
        ax.set_xlabel('n2 (SMA Lenta)', fontsize=9)
        ax.set_ylabel('n1 (SMA Rápida)', fontsize=9)
        ax.tick_params(labelsize=8)
    
    # Ocultar ejes sobrantes si num_markets < nrows*ncols
    for idx in range(num_markets, nrows * ncols):
        if idx < len(axes):
            axes[idx].set_visible(False)
    
    plt.tight_layout()
    
    # Guardar si se especificó ruta
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Mapas de calor guardados en: {save_path}")
    
    return fig, axes


def create_best_configs_summary(results_dict: dict, market_names: List[str], 
                                 market_categories: dict) -> pd.DataFrame:
    """
    Crea tabla resumen con las mejores configuraciones por activo.
    
    Parameters:
    -----------
    results_dict : dict
        Diccionario con {idx: DataFrame} de resultados por mercado
    market_names : list
        Nombres de los mercados
    market_categories : dict
        Diccionario con categorías de mercados {categoria: [indices]}
        
    Returns:
    --------
    pd.DataFrame
        DataFrame con mejores configuraciones ordenadas por retorno
    """
    best_configs = []
    
    for idx, market_name in enumerate(market_names):
        market_data = results_dict[idx]
        
        # Encontrar máximo
        max_val = market_data.max().max()
        max_pos = market_data.stack().idxmax()
        
        # Encontrar categoría
        categoria = [k for k, v in market_categories.items() if idx in v]
        categoria = categoria[0] if categoria else 'Sin categoría'
        
        best_configs.append({
            'Activo': market_name,
            'n1_óptimo': max_pos[0],
            'n2_óptimo': max_pos[1],
            'Retorno (%)': max_val,
            'Categoría': categoria
        })
    
    df_best = pd.DataFrame(best_configs)
    df_best = df_best.sort_values('Retorno (%)', ascending=False)
    
    return df_best
