"""
Script de ejemplo para ejecutar la estrategia MACD + ADX + EMA.

Este script demuestra cómo usar la nueva estructura modular del proyecto.
"""

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.kama_strategies import KAMACrossover
from src.utils.data_loader import load_crypto_data
from src.utils.optimization import walk_forward
from src.utils.plotting import plot_stats
import backtesting
import multiprocessing
import datetime as dt


def main():
    """Función principal."""
    print("="*60)
    print("Backtesting: Estrategia KAMA - Walk-Forward Optimization")
    print("="*60)
    
    # Cargar datos
    print("\n1. Cargando datos de BTC-USD...")
    btc_data = load_crypto_data(
        symbol='BTC-USD',
        start=dt.datetime(2015, 1, 1),
        end=dt.datetime(2025, 11, 26),
        interval='1d',
        normalize=True
    )
    print(f"   Datos cargados: {len(btc_data)} barras")
    print(f"   Período: {btc_data.index[0]} a {btc_data.index[-1]}")
    
    # Configurar multiprocessing para optimización
    backtesting.Pool = multiprocessing.Pool
    
    # Ejecutar walk-forward optimization
    print("\n2. Ejecutando optimización walk-forward...")
    print("   (Esto puede tomar varios minutos)")
    
    stats = walk_forward(
        btc_data,
        KAMACrossover,
        maximize='Sortino Ratio',
        constraint=lambda p: (
            p.n1 < p.n2 and 
            p.stop < p.profit
        )
    )
    
    # Graficar y guardar resultados
    print("\n3. Generando gráficos y guardando resultados...")
    plot_stats(stats, strategy_name="KAMACrossover")
    
    # Mostrar mejores parámetros
    print("\n" + "="*60)
    print("PARÁMETROS OPTIMIZADOS (último período)")
    print("="*60)
    
    best_params = stats[-1]._strategy._params
    print("\nParámetros optimizados:")
    for key, value in best_params.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*60)
    print("Optimización completada!")
    print("="*60)
    print("\nPara probar estos parámetros en intervalos de tiempo,")
    print("ejecuta: python scripts/test_kama_strategy.py")
    print("(Recuerda actualizar los parámetros en ese script)")


if __name__ == "__main__":
    main()
