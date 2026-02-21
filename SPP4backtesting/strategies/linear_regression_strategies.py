"""
Linear Regression Trading Strategies

This module contains trading strategies based on linear regression analysis.
Linear regression can be used to identify trends and potential reversal points
by analyzing the slope and position of the regression line.

The module includes:
- LinearRegressionStrategy: Trades based on linear regression slope

Linear regression strategies work well in trending markets but may generate
false signals in choppy/sideways conditions.

Example:
    Basic usage of LinearRegressionStrategy:
    
    >>> from strategies.linear_regression_strategies import LinearRegressionStrategy
    >>> from utils.data_loader import load_crypto_data
    >>> from backtesting import Backtest
    >>> 
    >>> data = load_crypto_data('BTC-USD', period='1y', normalize=True)
    >>> bt = Backtest(data, LinearRegressionStrategy, cash=10000, commission=0.001)
    >>> stats = bt.run()
"""

from backtesting.lib import crossover, resample_apply
import talib
from strategies.base_strategies import BaseStrategy

class LinearRegressionStrategy(BaseStrategy):
    """
    Linear Regression Slope Trading Strategy.
    
    This strategy uses linear regression to determine market trend direction.
    It calculates both the linear regression line and its slope to generate
    trading signals.
    
    The linear regression line represents the "best fit" line through recent
    price data. The slope indicates the direction and strength of the trend:
    - Positive slope: Uptrend (bullish)
    - Negative slope: Downtrend (bearish)
    - Slope near zero: Sideways market
    
    Attributes:
        period (int): Lookback period for linear regression calculation. Default is 20.
            Shorter periods are more responsive to recent price changes.
            Longer periods provide smoother, more stable trend identification.
    
    Optimization Ranges:
        period: 10 to 45 (regression calculation period)
    
    Trading Logic:
        - Long Entry: Regression slope > 0 (uptrend detected)
        - Short Entry: Regression slope < 0 (downtrend detected)
        - Position Management: Closes opposite positions before opening new ones
    
    Indicators Used:
        - LINEARREG: Linear regression line value
        - LINEARREG_SLOPE: Slope of the linear regression line
    
    Based on: bt_linear_regression.py (legacy implementation)
    
    Example:
        >>> bt = Backtest(data, LinearRegressionStrategy, cash=10000, commission=0.001)
        >>> stats = bt.run(period=20)
    """
    
    # Strategy parameter with default value
    period = 20  # Linear regression calculation period
    
    # Optimization parameter range
    opt_ranges = {
        'period': range(10, 50, 5)  # Period: 10 to 45 in steps of 5
    }
    
    def init(self):
        """
        Initialize strategy indicators.
        
        Creates two linear regression indicators:
        - linreg: The linear regression line (forecasted value)
        - linreg_slope: The slope of the regression line (trend direction)
        """
        # Linear regression line (forecasted price value)
        self.linreg = self.I(
            talib.LINEARREG,
            self.data.Close,
            timeperiod=self.period
        )
        
        # Linear regression slope (trend direction and strength)
        # Positive slope = uptrend, Negative slope = downtrend
        self.linreg_slope = self.I(
            talib.LINEARREG_SLOPE,
            self.data.Close,
            timeperiod=self.period
        )
    
    def next(self):
        """
        Execute trading logic on each bar.
        
        Trades based on the slope of the linear regression line.
        Positive slope indicates upward momentum, negative slope indicates
        downward momentum.
        """
        # Positive slope: Uptrend detected (buy signal)
        if self.linreg_slope > 0:
            # Close short position if exists
            if self.position.is_short:
                self.position.close()
            # Enter long position if not already in one
            if not self.position:
                self.buy()
        
        # Negative slope: Downtrend detected (sell signal)
        elif self.linreg_slope < 0:
            # Close long position if exists
            if self.position.is_long:
                self.position.close()
            # Enter short position if not already in one
            if not self.position:
                self.sell()
