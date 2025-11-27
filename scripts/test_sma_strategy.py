"""
Script para probar estrategia SMA con parámetros específicos en intervalos de tiempo.

Este script prueba parámetros optimizados (o manuales) en:
- Dataset completo
- Intervalos anuales
- Intervalos trimestrales
- Intervalos personalizados
"""

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.sma_strategies import BTSMAStrategy
from src.utils.data_loader import load_crypto_data
from src.utils.optimization import test_strategy_intervals
from src.utils.plotting import plot_interval_comparison, save_interval_results
import datetime as dt


def main():
    """Función principal."""
    print("="*60)
    print("Prueba de Estrategia SMA por Intervalos")
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
    
    # Parámetros a probar (puedes modificarlos aquí)
    print("\n2. Configurando parámetros de prueba...")
    
    # OPCIÓN 1: Usar parámetros optimizados de un run anterior
    # Modifica estos valores con los parámetros que obtuviste de run_sma_strategy.py
    test_params = {
        'n1': 10,      # Período SMA rápido
        'n2': 22,      # Período SMA lento
        'stop': 1,    # Stop loss %
        'profit': 62   # Take profit %
    }
    
    # OPCIÓN 2: Descomentar para usar parámetros por defecto
    # test_params = {
    #     'n1': 10,
    #     'n2': 30,
    #     'stop': 2,
    #     'profit': 4
    # }
    
    print("\nParámetros a probar:")
    for key, value in test_params.items():
        print(f"  {key}: {value}")
    
    # 3. Probar con intervalos anuales
    print("\n" + "="*60)
    print("3. Probando estrategia por intervalos ANUALES...")
    print("="*60)
    
    results_yearly = test_strategy_intervals(
        btc_data,
        BTSMAStrategy,
        test_params,
        interval_type='yearly'
    )
    
    save_interval_results(
        results_yearly['intervals'],
        results_yearly['full'],
        'BTSMAStrategy',
        'yearly',
        test_params
    )
    
    plot_interval_comparison(
        results_yearly['intervals'],
        results_yearly['full'],
        'BTSMAStrategy',
        'yearly'
    )
    
    # 4. Probar con intervalos trimestrales
    print("\n" + "="*60)
    print("4. Probando estrategia por intervalos TRIMESTRALES...")
    print("="*60)
    
    results_quarterly = test_strategy_intervals(
        btc_data,
        BTSMAStrategy,
        test_params,
        interval_type='quarterly'
    )
    
    save_interval_results(
        results_quarterly['intervals'],
        results_quarterly['full'],
        'BTSMAStrategy',
        'quarterly',
        test_params
    )
    
    plot_interval_comparison(
        results_quarterly['intervals'],
        results_quarterly['full'],
        'BTSMAStrategy',
        'quarterly'
    )
    
    # 5. Probar con intervalos personalizados (180 días)
    print("\n" + "="*60)
    print("5. Probando estrategia por intervalos PERSONALIZADOS (180 días)...")
    print("="*60)
    
    results_custom = test_strategy_intervals(
        btc_data,
        BTSMAStrategy,
        test_params,
        interval_type='custom',
        custom_days=180
    )
    
    save_interval_results(
        results_custom['intervals'],
        results_custom['full'],
        'BTSMAStrategy',
        'custom_180d',
        test_params
    )
    
    plot_interval_comparison(
        results_custom['intervals'],
        results_custom['full'],
        'BTSMAStrategy',
        'custom_180d'
    )
    
    print("\n" + "="*60)
    print("Pruebas completadas!")
    print("="*60)
    print("\nResultados guardados en:")
    print("  - results/csv/")
    print("  - results/plots/")


if __name__ == "__main__":
    main()
