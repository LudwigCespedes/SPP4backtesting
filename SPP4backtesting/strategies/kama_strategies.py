"""
KAMA (Kaufman Adaptive Moving Average) Trading Strategies

This module contains trading strategies based on the Kaufman Adaptive Moving Average (KAMA).
KAMA is a moving average designed to account for market noise and volatility. It adapts its
smoothing constant based on market conditions - moving faster in trending markets and slower
in choppy/sideways markets.

The module includes:
- KamaStrategy: Price crossover with KAMA
- KAMACrossover: Dual KAMA crossover with stop-loss and take-profit

KAMA is particularly useful in volatile markets where traditional moving averages may
generate too many false signals.

Example:
    Basic usage of KamaStrategy:
    
    >>> from strategies.kama_strategies import KamaStrategy
    >>> from utils.data_loader import load_crypto_data
    >>> from backtesting import Backtest
    >>> 
    >>> data = load_crypto_data('BTC-USD', period='1y', normalize=True)
    >>> bt = Backtest(data, KamaStrategy, cash=10000, commission=0.001)
    >>> stats = bt.run()
"""

from backtesting import Strategy
from backtesting.lib import crossover
import talib
from base_strategies import BaseStrategy

class KamaStrategy(BaseStrategy):
    """
    KAMA Price Crossover Strategy.
    
    This strategy uses the Kaufman Adaptive Moving Average (KAMA) as a dynamic
    support/resistance level. Trades are generated when price crosses above or
    below the KAMA line.
    
    KAMA adapts to market volatility:
    - In trending markets: KAMA follows price more closely
    - In choppy markets: KAMA smooths out noise
    
    Attributes:
        period (int): Period for KAMA calculation. Default is 10.
            Shorter periods make KAMA more responsive.
            Longer periods make KAMA smoother.
    
    Optimization Ranges:
        period: 5 to 45 (KAMA calculation period)
    
    Trading Logic:
        - Long Entry: Price crosses above KAMA (bullish signal)
        - Short Entry: Price crosses below KAMA (bearish signal)
        - Position Management: Closes opposite positions before opening new ones
    
    Based on: bt_kama.py (legacy implementation)
    
    Example:
        >>> bt = Backtest(data, KamaStrategy, cash=10000, commission=0.001)
        >>> stats = bt.run(period=10)
    """
    
    # Strategy parameter with default value
    period = 10  # KAMA calculation period
    
    # Optimization parameter range
    opt_ranges = {
        'period': range(5, 50, 5)  # Period: 5 to 45 in steps of 5
    }
    
    def init(self):
        """
        Initialize strategy indicators.
        
        Creates the KAMA indicator which adapts to market volatility.
        """
        # Kaufman Adaptive Moving Average
        self.kama = self.I(talib.KAMA, self.data.Close, timeperiod=self.period)
    
    def next(self):
        """
        Execute trading logic on each bar.
        
        Trades based on price crossovers with KAMA. The adaptive nature of KAMA
        helps reduce false signals in choppy markets.
        """
        # Bullish crossover: Price crosses above KAMA
        if crossover(self.data.Close, self.kama):
            # Close short position if exists
            if self.position.is_short:
                self.position.close()
            # Enter long position
            self.buy()
        
        # Bearish crossover: Price crosses below KAMA
        elif crossover(self.kama, self.data.Close):
            # Close long position if exists
            if self.position.is_long:
                self.position.close()
            # Enter short position
            self.sell()


class KAMACrossover(Strategy):
    """
    Dual KAMA Crossover Strategy with Stop-Loss and Take-Profit.
    
    This strategy uses two KAMA indicators of different periods to generate
    trading signals. Similar to dual SMA crossover, but with the adaptive
    properties of KAMA to better handle market volatility.
    
    Includes risk management through dynamic stop-loss and take-profit levels.
    
    Attributes:
        n1 (int): Period for fast KAMA. Default is 11.
        n2 (int): Period for slow KAMA. Default is 22.
        stop (int): Stop-loss percentage. Default is 10 (10% from entry).
        profit (int): Take-profit percentage. Default is 20 (20% from entry).
    
    Optimization Ranges:
        n1: 5 to 47 (fast KAMA period)
        n2: 10 to 98 (slow KAMA period)
        stop: 2 to 18 (stop-loss percentage)
        profit: 4 to 98 (take-profit percentage)
    
    Trading Logic:
        - Long Entry: Fast KAMA crosses above slow KAMA (golden cross)
        - Short Entry: Fast KAMA crosses below slow KAMA (death cross)
        - Risk Management: Dynamic SL/TP on all positions
    
    Note:
        Total optimization combinations: 9 × 9 × 9 × 9 = 6,561 (manageable)
    
    Example:
        >>> bt = Backtest(data, KAMACrossover, cash=10000, commission=0.001)
        >>> stats = bt.run(n1=11, n2=22, stop=10, profit=20)
    """
    
    # Strategy parameters with default values
    n1 = 11        # Fast KAMA period
    n2 = 22        # Slow KAMA period
    stop = 10      # Stop-loss percentage
    profit = 20    # Take-profit percentage
    
    # Optimization parameter ranges
    opt_ranges = {
        'n1': range(5, 50, 2),      # Fast KAMA: 5 to 47 (9 values)
        'n2': range(10, 100, 2),    # Slow KAMA: 10 to 98 (9 values)
        'stop': range(2, 20, 2),    # Stop-loss: 2% to 18% (9 values)
        'profit': range(4, 100, 2)  # Take-profit: 4% to 98% (9 values)
    }
    # Total combinations: 9 × 9 × 9 × 9 = 6,561 (manageable)

    def init(self):
        """
        Initialize strategy indicators.
        
        Creates two KAMA indicators:
        - kama1: Fast KAMA for short-term adaptive trend
        - kama2: Slow KAMA for long-term adaptive trend
        """
        # Fast KAMA for short-term adaptive trend
        self.kama1 = self.I(talib.KAMA, self.data.Close, self.n1)
        # Slow KAMA for long-term adaptive trend
        self.kama2 = self.I(talib.KAMA, self.data.Close, self.n2)

    def next(self):
        """
        Execute trading logic on each bar.
        
        Trades on KAMA crossovers with stop-loss and take-profit protection.
        The adaptive nature of KAMA helps the strategy perform better across
        different market conditions.
        """
        # Bullish crossover: Fast KAMA crosses above Slow KAMA
        if crossover(self.kama1, self.kama2):
            # Close any existing position
            self.position.close()
            # Enter long position with SL/TP
            self.buy(
                sl=(self.data.Close - self.data.Close * (self.stop / 100)),
                tp=(self.data.Close + self.data.Close * (self.profit / 100))
            )
        
        # Bearish crossover: Fast KAMA crosses below Slow KAMA
        elif crossover(self.kama2, self.kama1):
            # Close any existing position
            self.position.close()
            # Enter short position with SL/TP
            self.sell(
                sl=(self.data.Close + self.data.Close * (self.stop / 100)),
                tp=(self.data.Close - self.data.Close * (self.profit / 100))
            )