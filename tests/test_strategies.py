"""
Tests básicos para las estrategias.
"""

import sys
import os
import unittest

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.strategies.macd_strategies import MacdStrategy, MacdAdxEmaStrategy
from src.strategies.sma_strategies import BTSMAStrategy
from src.strategies.momentum_strategies import KamaStrategy
import pandas as pd
import numpy as np


class TestStrategies(unittest.TestCase):
    """Tests para verificar que las estrategias se pueden instanciar."""
    
    def setUp(self):
        """Crear datos de prueba."""
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        # Generar datos OHLC sintéticos
        close = 100 + np.cumsum(np.random.randn(100) * 2)
        high = close + np.abs(np.random.randn(100))
        low = close - np.abs(np.random.randn(100))
        open_price = close + np.random.randn(100) * 0.5
        
        self.test_data = pd.DataFrame({
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close,
        }, index=dates)
    
    def test_macd_strategy_has_opt_ranges(self):
        """Verificar que MacdStrategy tiene opt_ranges."""
        self.assertTrue(hasattr(MacdStrategy, 'opt_ranges'))
        self.assertIsInstance(MacdStrategy.opt_ranges, dict)
    
    def test_macd_adx_ema_strategy_has_opt_ranges(self):
        """Verificar que MacdAdxEmaStrategy tiene opt_ranges."""
        self.assertTrue(hasattr(MacdAdxEmaStrategy, 'opt_ranges'))
        self.assertIsInstance(MacdAdxEmaStrategy.opt_ranges, dict)
    
    def test_btsma_strategy_has_opt_ranges(self):
        """Verificar que BTSMAStrategy tiene opt_ranges."""
        self.assertTrue(hasattr(BTSMAStrategy, 'opt_ranges'))
        self.assertIsInstance(BTSMAStrategy.opt_ranges, dict)
    
    def test_kama_strategy_has_opt_ranges(self):
        """Verificar que KamaStrategy tiene opt_ranges."""
        self.assertTrue(hasattr(KamaStrategy, 'opt_ranges'))
        self.assertIsInstance(KamaStrategy.opt_ranges, dict)
    
    def test_strategies_can_be_imported(self):
        """Verificar que todas las estrategias se pueden importar."""
        from src.strategies.macd_strategies import (
            MacdAdxEmaStrategy, MacdAdxStrategy, MacdStrategy, MacdAdxSmaStrategy
        )
        from src.strategies.sma_strategies import BTSMAStrategy, SmaAdxStrategy
        from src.strategies.momentum_strategies import (
            MomentumStrategy, KamaStrategy, LinearRegressionStrategy
        )
        from src.strategies.arbitrage_strategies import GridStrategy, UsdtUsdcArbitrage
        
        # Si llegamos aquí, todos los imports funcionaron
        self.assertTrue(True)


class TestUtils(unittest.TestCase):
    """Tests para las utilidades."""
    
    def test_data_loader_imports(self):
        """Verificar que data_loader se puede importar."""
        from src.utils.data_loader import (
            load_crypto_data, load_stock_data, load_multiple_symbols
        )
        self.assertTrue(True)
    
    def test_optimization_imports(self):
        """Verificar que optimization se puede importar."""
        from src.utils.optimization import walk_forward, optimize_auto, run_simple_backtest
        self.assertTrue(True)
    
    def test_plotting_imports(self):
        """Verificar que plotting se puede importar."""
        from src.utils.plotting import plot_stats, save_results, print_summary
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
