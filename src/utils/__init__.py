"""
Módulo de utilidades para backtesting.
"""

from src.utils.data_loader import (
    load_crypto_data,
    load_stock_data,
    load_multiple_symbols
)
from src.utils.optimization import (
    walk_forward,
    optimize_auto
)
from src.utils.plotting import (
    plot_stats,
    save_results
)

__all__ = [
    'load_crypto_data',
    'load_stock_data',
    'load_multiple_symbols',
    'walk_forward',
    'optimize_auto',
    'plot_stats',
    'save_results',
]
