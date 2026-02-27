
from backtesting import Strategy , Backtest
from backtesting.lib import crossover
import talib
from .base_strategies import BaseStrategy
import datetime as dt
import multiprocessing
from backtesting.lib import FractionalBacktest

class BTSMAStrategy(BaseStrategy):
    # Strategy parameters with default values
    n1 = 11      # Fast SMA period
    n2 = 22      # Slow SMA period
    stop = 5     # Stop-loss percentage
    
    # Optimization parameter ranges
    opt_ranges = {
        'n1': range(2, 102, 1),    # Fast SMA period: 2 to 100
        'n2': range(2,205, 1),    # Slow SMA period: 2 to 200
        'stop': range(2, 20, 1),   # Stop-loss: 2% to 79%
    }
    
    def init(self):
        """
        Initialize strategy indicators.
        
        Creates two SMA indicators:
        - sma1: Fast (short-term) moving average
        - sma2: Slow (long-term) moving average
        """
        # Fast SMA for short-term trend
        self.sma1 = self.I(talib.SMA, self.data.Close, self.n1)
        # Slow SMA for long-term trend
        self.sma2 = self.I(talib.SMA, self.data.Close, self.n2)
    
    def next(self):
        """
        Execute trading logic on each bar.
        
        Checks for SMA crossovers and executes trades with stop-loss protection.
        Closes any existing position before opening a new one in the opposite direction.
        """
        # Bullish crossover: Fast SMA crosses above Slow SMA (Golden Cross)
        if crossover(self.sma1, self.sma2):
            # Close any existing position
            self.position.close()
            # Enter long position with stop-loss
            self.buy(
                sl=(self.data.Close - self.data.Close * (self.stop / 100)),
            )
        
        # Bearish crossover: Slow SMA crosses above Fast SMA (Death Cross)
        elif crossover(self.sma2, self.sma1):
            # Close any existing position
            self.position.close()
            # Enter short position with stop-loss
            self.sell(
                sl=(self.data.Close + self.data.Close * (self.stop / 100)),
            )


class SmaAdxStrategy(BaseStrategy):
    """
    SMA Crossover Strategy with ADX Trend Strength Filter.
    
    This strategy combines Simple Moving Average (SMA) crossovers for trend direction
    with the Average Directional Index (ADX) for trend strength filtering. Trades are
    only executed when ADX indicates a strong trending market, helping to avoid
    false signals in sideways/choppy markets.
    
    Attributes:
        smafast (int): Period for the fast SMA. Default is 20.
        smaslow (int): Period for the slow SMA. Default is 50.
        adxperiod (int): Period for ADX calculation. Default is 14.
        adxpass (int): Minimum ADX value to allow trading. Default is 25.
            ADX > 25 typically indicates a trending market.
            ADX < 25 suggests a weak trend or sideways market.
    
    Optimization Ranges:
        smafast: 10 to 45 (fast SMA period)
        smaslow: 40 to 190 (slow SMA period)
        adxperiod: 10 to 19 (ADX calculation period)
        adxpass: 20 to 35 (minimum ADX threshold)
    
    Trading Logic:
        - Only trade when ADX > adxpass (strong trend)
        - Long Entry: Fast SMA crosses above slow SMA AND ADX > threshold
        - Short Entry: Fast SMA crosses below slow SMA AND ADX > threshold
        - Exit: Close positions when ADX falls below threshold (weak trend)
    
    Based on: bt_sma_adx.py (legacy implementation)
    
    Example:
        >>> bt = Backtest(data, SmaAdxStrategy, cash=10000, commission=0.001)
        >>> stats = bt.run(smafast=15, smaslow=50, adxperiod=14, adxpass=25)
    """
    
    # Strategy parameters with default values
    smafast = 20      # Fast SMA period
    smaslow = 50      # Slow SMA period
    adxperiod = 14    # ADX calculation period
    adxpass = 25      # Minimum ADX for trading (trend strength threshold)
    
    # Optimization parameter ranges
    opt_ranges = {
        'smafast': range(10, 50, 5),     # Fast SMA: 10 to 45
        'smaslow': range(40, 200, 10),   # Slow SMA: 40 to 190
        'adxperiod': range(10, 20),      # ADX period: 10 to 19
        'adxpass': range(20, 40, 5)      # ADX threshold: 20 to 35
    }
    
    def init(self):
        """
        Initialize strategy indicators.
        
        Creates three indicators:
        - sma_fast: Fast SMA for short-term trend
        - sma_slow: Slow SMA for long-term trend
        - adx: Average Directional Index for trend strength
        """
        # Fast SMA for short-term trend direction
        self.sma_fast = self.I(talib.SMA, self.data.Close, self.smafast)
        # Slow SMA for long-term trend direction
        self.sma_slow = self.I(talib.SMA, self.data.Close, self.smaslow)
        # ADX for trend strength measurement (requires High, Low, Close)
        self.adx = self.I(
            talib.ADX,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.adxperiod
        )
    
    def next(self):
        """
        Execute trading logic on each bar.
        
        Only trades when ADX indicates a strong trend. Closes positions when
        the market becomes choppy or sideways (ADX below threshold).
        """
        # Only trade when trend is strong (ADX above threshold)
        if self.adx > self.adxpass:
            # Bullish crossover: Fast SMA crosses above Slow SMA
            if crossover(self.sma_fast, self.sma_slow):
                # Close short position if exists
                if self.position.is_short:
                    self.position.close()
                # Enter long position
                self.buy()
            
            # Bearish crossover: Slow SMA crosses above Fast SMA
            elif crossover(self.sma_slow, self.sma_fast):
                # Close long position if exists
                if self.position.is_long:
                    self.position.close()
                # Enter short position
                self.sell()
        else:
            # Close all positions when trend is weak (sideways market)
            # This helps avoid losses in choppy, non-trending conditions
            self.position.close()



