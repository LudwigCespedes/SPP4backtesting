"""
Script de ejemplo para ejecutar la estrategia SMA simple.

Demuestra cómo ejecutar un backtest básico sin optimización.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.sma_strategies import BTSMAStrategy
from src.utils.data_loader import load_crypto_data
from src.utils.plotting import print_summary
from backtesting import Backtest
import datetime as dt


def main():
    """Función principal."""
    print("="*60)
    print("Backtesting: Estrategia SMA")
    print("="*60)
    
    # Cargar datos
    print("\n1. Cargando datos de BTC-USD...")
    btc_data = load_crypto_data(
        symbol='BTC-USD',
        start=dt.datetime(2024, 1, 1),
        end=dt.datetime(2025, 11, 17),
        interval='1d',
        normalize=True
    )
    print(f"   Datos cargados: {len(btc_data)} barras")
    
    # Ejecutar backtest
    print("\n2. Ejecutando backtest...")
    bt = Backtest(btc_data, BTSMAStrategy, cash=10, commission=0.01)
    stats = bt.run()
    
    # Mostrar resultados
    print_summary(stats)
    
    # Generar gráfico interactivo
    print("\n3. Generando gráfico interactivo...")
    bt.plot(filename='results/html/BTSMA_simple.html')
    print("   Gráfico guardado en: results/html/BTSMA_simple.html")
    
    print("\n" + "="*60)
    print("Proceso completado!")
    print("="*60)


if __name__ == "__main__":
    main()
