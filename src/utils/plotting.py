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
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    # Guardar CSV y PNG con nombres descriptivos
    csv_path = os.path.join(csv_dir, f"{strategy_name}_{timestamp}.csv")
    png_path = os.path.join(plots_dir, f"{strategy_name}_{timestamp}.png")
    
    stats_df.to_csv(csv_path)
    plt.savefig(png_path)
    plt.show()
    
    print(f"\nResultados guardados:")
    print(f"  CSV: {csv_path}")
    print(f"  PNG: {png_path}")


def save_results(
    stats: Any,
    strategy_name: str,
    save_dir: str = "results",
    save_html: bool = True,
    save_csv: bool = True
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
