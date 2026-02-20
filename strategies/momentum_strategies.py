"""
Momentum-Based Trading Strategies

This module contains trading strategies based on momentum indicators. Momentum strategies
attempt to capitalize on the continuation of existing market trends by measuring the
rate of price change.

The module includes:
- MomentumStrategy: Uses the Momentum indicator to detect trend changes

Momentum indicators measure the speed of price movements and can help identify
overbought/oversold conditions and potential trend reversals.

Example:
    Basic usage of MomentumStrategy:
    
    >>> from strategies.momentum_strategies import MomentumStrategy
    >>> from utils.data_loader import load_crypto_data
    >>> from backtesting import Backtest
    >>> 
    >>> data = load_crypto_data('BTC-USD', period='1y', normalize=True)
    >>> bt = Backtest(data, MomentumStrategy, cash=10000, commission=0.001)
    >>> stats = bt.run()
"""

from backtesting import Strategy
from backtesting.lib import crossover
import talib
import numpy as np
from base_strategies import BaseStrategy

class MomentumStrategy(BaseStrategy):
    """
    Momentum Indicator Trading Strategy.
    
    This strategy uses the Momentum indicator (rate of change) to detect changes
    in price trends. The momentum indicator measures the amount that a security's
    price has changed over a given time period.
    
    Attributes:
        period (int): Lookback period for momentum calculation. Default is 14.
        threshold (int): Momentum threshold for trade signals. Default is 0.
            Positive momentum above threshold suggests uptrend.
            Negative momentum below -threshold suggests downtrend.
    
    Optimization Ranges:
        period: 5 to 29 (momentum calculation period)
        threshold: -10 to 9 (momentum threshold for signals)
    
    Trading Logic:
        - Long Entry: Momentum > threshold (positive momentum)
        - Short Entry: Momentum < -threshold (negative momentum)
        - Position Management: Closes opposite positions before opening new ones
    
    Based on: bt_mom.py (legacy implementation)
    
    Example:
        >>> bt = Backtest(data, MomentumStrategy, cash=10000, commission=0.001)
        >>> stats = bt.run(period=14, threshold=0)
    """
    
    # Strategy parameters with default values
    period = 14       # Momentum calculation period
    threshold = 0     # Momentum threshold for signals
    
    # Optimization parameter ranges
    opt_ranges = {
        'period': range(5, 30),      # Period: 5 to 29
        'threshold': range(-10, 10)  # Threshold: -10 to 9
    }
    
    def init(self):
        """
        Initialize strategy indicators.
        
        Creates the Momentum indicator which measures the rate of price change
        over the specified period.
        """
        # Momentum indicator: current price - price N periods ago
        self.momentum = self.I(talib.MOM, self.data.Close, timeperiod=self.period)
    
    def next(self):
        """
        Execute trading logic on each bar.
        
        Trades based on momentum crossing above/below the threshold.
        Positive momentum suggests buying pressure, negative suggests selling pressure.
        """
        # Positive momentum: Buy signal (upward price movement)
        if self.momentum > self.threshold:
            # Close short position if exists
            if self.position.is_short:
                self.position.close()
            # Enter long position if not already in one
            if not self.position:
                self.buy()
        
        # Negative momentum: Sell signal (downward price movement)
        elif self.momentum < -self.threshold:
            # Close long position if exists
            if self.position.is_long:
                self.position.close()
            # Enter short position if not already in one
            if not self.position:
                self.sell()

