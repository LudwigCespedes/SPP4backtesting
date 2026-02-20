"""
Base Strategy Module

This module provides an abstract base class for all trading strategies in the backtesting framework.
It defines a common interface and helper methods that all strategies must implement.

The BaseStrategy class extends backtesting.Strategy and enforces a consistent structure
for strategy development, including:
- Standardized initialization via init()
- Trading logic implementation via next()
- Optimization parameter ranges via opt_ranges
- Parameter introspection methods

Example:
    Creating a custom strategy by inheriting from BaseStrategy:
    
    >>> from strategies.base_strategies import BaseStrategy
    >>> import talib
    >>> 
    >>> class MyStrategy(BaseStrategy):
    ...     # Define strategy parameters
    ...     period = 20
    ...     
    ...     # Define optimization ranges
    ...     opt_ranges = {
    ...         'period': range(10, 50, 5)
    ...     }
    ...     
    ...     def init(self):
    ...         '''Initialize indicators'''
    ...         self.sma = self.I(talib.SMA, self.data.Close, self.period)
    ...     
    ...     def next(self):
    ...         '''Trading logic'''
    ...         if self.data.Close[-1] > self.sma[-1]:
    ...             self.buy()
    ...         elif self.data.Close[-1] < self.sma[-1]:
    ...             self.position.close()

Classes:
    BaseStrategy: Abstract base class for all trading strategies
"""

from backtesting import Strategy
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseStrategy(Strategy, ABC):
    """
    Abstract base class for all trading strategies.
    
    This class provides a common interface and structure for implementing trading strategies
    in the backtesting framework. All custom strategies should inherit from this class
    and follow the required implementation pattern.
    
    Requirements for child classes:
        1. Inherit from BaseStrategy
        2. Define the opt_ranges class attribute as a dictionary mapping parameter names
           to their optimization ranges (e.g., range objects, lists of values)
        3. Implement the init() method to initialize indicators and strategy state
        4. Implement the next() method to define trading logic executed on each bar
    
    Attributes:
        opt_ranges (Dict[str, Any]): Dictionary mapping parameter names to their 
            optimization ranges. This is used by the optimization engine to explore
            different parameter combinations. Must be overridden in child classes.
    
    Example:
        >>> class MyStrategy(BaseStrategy):
        ...     # Strategy parameters
        ...     fast_period = 10
        ...     slow_period = 20
        ...     
        ...     # Optimization ranges
        ...     opt_ranges = {
        ...         'fast_period': range(5, 20, 1),
        ...         'slow_period': range(15, 50, 5)
        ...     }
        ...     
        ...     def init(self):
        ...         # Initialize indicators
        ...         pass
        ...     
        ...     def next(self):
        ...         # Trading logic
        ...         pass
    """
    
    # This attribute must be overridden in each strategy subclass
    opt_ranges: Dict[str, Any] = {}
    
    @abstractmethod
    def init(self):
        """
        Initialize strategy indicators and variables.
        
        This method is called once at the start of the backtest, before any trading
        occurs. Use it to initialize technical indicators, set up data structures,
        and prepare any state needed for the strategy.
        
        Must be implemented by each strategy subclass.
        
        Example:
            >>> def init(self):
            ...     # Initialize moving averages
            ...     self.sma_fast = self.I(talib.SMA, self.data.Close, self.fast_period)
            ...     self.sma_slow = self.I(talib.SMA, self.data.Close, self.slow_period)
            ...     # Initialize RSI
            ...     self.rsi = self.I(talib.RSI, self.data.Close, 14)
        """
        pass
    
    @abstractmethod
    def next(self):
        """
        Execute trading logic on each new bar.
        
        This method is called for each bar in the dataset, from oldest to newest.
        Implement your trading logic here, including entry and exit signals,
        position management, and risk controls.
        
        Must be implemented by each strategy subclass.
        
        Note:
            - Use self.buy() to open long positions
            - Use self.sell() to open short positions
            - Use self.position.close() to close current position
            - Access current bar data via self.data (e.g., self.data.Close[-1])
            - Access indicator values via their references (e.g., self.sma[-1])
        
        Example:
            >>> def next(self):
            ...     # Buy signal: fast SMA crosses above slow SMA
            ...     if crossover(self.sma_fast, self.sma_slow):
            ...         if self.position.is_short:
            ...             self.position.close()
            ...         self.buy()
            ...     # Sell signal: fast SMA crosses below slow SMA
            ...     elif crossover(self.sma_slow, self.sma_fast):
            ...         if self.position.is_long:
            ...             self.position.close()
            ...         self.sell()
        """
        pass
    
    def get_params(self) -> Dict[str, Any]:
        """
        Get the current parameter values of the strategy.
        
        Returns a dictionary containing all parameters defined in opt_ranges
        with their current values. Useful for logging, debugging, and result analysis.
        
        Returns:
            Dict[str, Any]: Dictionary mapping parameter names to their current values.
                Only includes parameters that are defined in opt_ranges and exist
                as attributes on the strategy instance.
        
        Example:
            >>> strategy = MyStrategy()
            >>> params = strategy.get_params()
            >>> print(params)
            {'fast_period': 10, 'slow_period': 20}
        """
        params = {}
        for key in self.opt_ranges.keys():
            if hasattr(self, key):
                params[key] = getattr(self, key)
        return params
    
    def __repr__(self) -> str:
        """
        Return a string representation of the strategy.
        
        Provides a human-readable representation showing the strategy class name
        and its current parameter values.
        
        Returns:
            str: String representation in the format "StrategyName(param1=value1, param2=value2)"
        
        Example:
            >>> strategy = MyStrategy()
            >>> print(strategy)
            MyStrategy(fast_period=10, slow_period=20)
        """
        params = self.get_params()
        params_str = ", ".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.__class__.__name__}({params_str})"
