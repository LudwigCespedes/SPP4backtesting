"""
Módulo de estrategias de trading para backtesting.
"""

from src.strategies.base_strategies import BaseStrategy
from src.strategies.macd_strategies import (
    MacdAdxEmaStrategy,
    MacdAdxStrategy,
    MacdStrategy,
    MacdAdxSmaStrategy
)
from src.strategies.sma_strategies import (
    BTSMAStrategy,
    SmaAdxStrategy
)
from src.strategies.momentum_strategies import (
    MomentumStrategy
)
from src.strategies.grid_strategies import (
    GridStrategy
)
from src.strategies.arbitrage_strategies import (
    UsdtUsdcArbitrage
)
from src.strategies.linear_regression_strategies import (
    LinearRegressionStrategy
)
from src.strategies.kama_strategies import (
    KAMACrossover,
    KamaStrategy
)

__all__ = [
    'BaseStrategy',
    'MacdAdxEmaStrategy',
    'MacdAdxStrategy',
    'MacdStrategy',
    'MacdAdxSmaStrategy',
    'BTSMAStrategy',
    'SmaAdxStrategy',
    'MomentumStrategy',
    'LinearRegressionStrategy',
    'GridStrategy',
    'UsdtUsdcArbitrage',
    'KAMACrossover',
    'KamaStrategy'
]
