"""
Módulo de estrategias de trading para backtesting.
"""

from src.strategies.base import BaseStrategy
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
    MomentumStrategy,
    KamaStrategy,
    LinearRegressionStrategy
)
from src.strategies.grid_strategies import (
    GridStrategy
)
from src.strategies.arbitrage_strategies import (
    UsdtUsdcArbitrage
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
    'KamaStrategy',
    'LinearRegressionStrategy',
    'GridStrategy',
    'UsdtUsdcArbitrage',
]
