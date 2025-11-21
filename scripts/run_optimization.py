"""
Script para ejecutar optimización en múltiples estrategias.

Permite comparar el rendimiento de diferentes estrategias.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.macd_strategies import MacdStrategy, MacdAdxStrategy
from src.strategies.sma_strategies import BTSMAStrategy, SmaAdxStrategy
from src.strategies.momentum_strategies import KamaStrategy
from src.utils.data_loader import load_crypto_data
from src.utils.optimization import run_simple_backtest
from backtesting import Backtest
import pandas as pd
import datetime as dt


def main():
    """Función principal."""
    print("="*60)
    print("Comparación de Estrategias")
    print("="*60)
    
    # Cargar datos
    print("\n1. Cargando datos de BTC-USD...")
    btc_data = load_crypto_data(
        symbol='BTC-USD',
        start=dt.datetime(2024, 1, 1),
        interval='1d',
        normalize=True
    )
    
    # Lista de estrategias a probar
    strategies = [
        ('MACD Simple', MacdStrategy),
        ('MACD + ADX', MacdAdxStrategy),
        ('SMA Crossover', BTSMAStrategy),
        ('SMA + ADX', SmaAdxStrategy),
        ('KAMA', KamaStrategy),
    ]
    
    results = []
    
    # Ejecutar cada estrategia
    print("\n2. Ejecutando backtests...")
    for name, strategy in strategies:
        print(f"\n   Probando: {name}...")
        try:
            stats = run_simple_backtest(btc_data, strategy, cash=10, commission=0.01)
            results.append({
                'Estrategia': name,
                'Return [%]': stats['Return [%]'],
                'Sharpe Ratio': stats['Sharpe Ratio'],
                'Sortino Ratio': stats['Sortino Ratio'],
                'Max. Drawdown [%]': stats['Max. Drawdown [%]'],
                'Win Rate [%]': stats['Win Rate [%]'],
                '# Trades': stats['# Trades'],
            })
        except Exception as e:
            print(f"      Error: {e}")
    
    # Mostrar resultados comparativos
    print("\n3. Resultados Comparativos:")
    print("="*60)
    
    df = pd.DataFrame(results)
    df = df.sort_values('Sortino Ratio', ascending=False)
    
    print(df.to_string(index=False))
    
    # Guardar resultados
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f'results/csv/comparison_{timestamp}.csv'
    df.to_csv(csv_path, index=False)
    
    print(f"\n4. Resultados guardados en: {csv_path}")
    print("\n" + "="*60)
    print("Proceso completado!")
    print("="*60)


if __name__ == "__main__":
    main()
