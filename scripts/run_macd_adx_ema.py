"""
Script de ejemplo para ejecutar la estrategia MACD + ADX + EMA.

Este script demuestra cómo usar la nueva estructura modular del proyecto.
"""

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.macd_strategies import MacdAdxEmaStrategy
from src.utils.data_loader import load_crypto_data
from src.utils.optimization import walk_forward
from src.utils.plotting import plot_stats
import backtesting
import multiprocessing
import datetime as dt


def main():
    """Función principal."""
    print("="*60)
    print("Backtesting: Estrategia MACD + ADX + EMA")
    print("="*60)
    
    # Cargar datos
    print("\n1. Cargando datos de BTC-USD...")
    btc_data = load_crypto_data(
        symbol='BTC-USD',
        period='max',
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
        MacdAdxEmaStrategy,
        maximize='Alpha [%]',
        constraint=lambda p: (
            p.macdfast < p.macdslow and 
            p.emafast < p.emalow and 
            p.adxperiod < p.adxpass
        )
    )
    
    # Graficar y guardar resultados
    print("\n3. Generando gráficos y guardando resultados...")
    plot_stats(stats, strategy_name="MacdAdxEma")
    
    print("\n" + "="*60)
    print("Proceso completado!")
    print("="*60)


if __name__ == "__main__":
    main()
