"""
Grid Trading Strategies

This module contains grid trading strategies. Grid trading is a systematic approach
that places buy and sell orders at predefined price levels (grids) to profit from
market volatility within a range.

The module includes:
- GridStrategy: Places buy orders at lower price levels and sells at higher levels

Grid trading works best in ranging/sideways markets with predictable volatility.
It can be risky in strongly trending markets if not properly managed.

Example:
    Basic usage of GridStrategy:
    
    >>> from strategies.grid_strategies import GridStrategy
    >>> from utils.data_loader import load_crypto_data
    >>> from backtesting import Backtest
    >>> 
    >>> data = load_crypto_data('BTC-USD', period='1y', normalize=True)
    >>> bt = Backtest(data, GridStrategy, cash=10000, commission=0.001)
    >>> stats = bt.run()
"""

from base_strategies import BaseStrategy
import talib


class GridStrategy(BaseStrategy):
    """
    Grid Trading Strategy.
    
    This strategy places buy orders at predefined price levels below the initial price
    and automatically sells when price reaches the profit target. It's designed to
    profit from price oscillations within a range.
    
    The strategy creates a grid of buy levels, each separated by a percentage distance.
    When price hits a grid level, a buy order is executed with a take-profit target
    set at grid_profit percentage above the entry.
    
    Attributes:
        grid_profit (int): Profit percentage per grid level. Default is 1 (1%).
        grid_buy (int): Number of buy grid levels to create. Default is 10.
    
    Optimization Ranges:
        grid_profit: 1 to 4 (profit percentage per grid)
        grid_buy: 5 to 19 (number of grid levels)
    
    Trading Logic:
        - Initial Setup: Creates grid levels below starting price
        - Buy Signal: Price reaches a grid level
        - Sell Signal: Take-profit target is hit (grid_profit % above entry)
        - Grid Spacing: Each level is grid_profit % below the previous level
    
    Note:
        This is a simplified grid implementation. Production grid bots typically
        include features like:
        - Grid rebalancing
        - Multiple simultaneous positions
        - Stop-loss for the entire grid
        - Dynamic grid adjustment based on volatility
    
    Based on: bt_grid.py (legacy implementation)
    
    Example:
        >>> bt = Backtest(data, GridStrategy, cash=10000, commission=0.001)
        >>> stats = bt.run(grid_profit=2, grid_buy=10)
    """
    
    # Strategy parameters with default values
    grid_profit = 1   # Profit percentage per grid level
    grid_buy = 10     # Number of buy grid levels
    
    # Optimization parameter ranges
    opt_ranges = {
        'grid_profit': range(1, 5),   # Profit: 1% to 4%
        'grid_buy': range(5, 20)      # Grid levels: 5 to 19
    }
    
    def init(self):
        """
        Initialize the strategy.
        
        Sets up empty grid levels list and initial price placeholder.
        Grid levels will be calculated on the first bar.
        """
        # List to store grid price levels
        self.grid_levels = []
        # Initial price (set on first bar)
        self.initial_price = None
    
    def next(self):
        """
        Execute trading logic on each bar.
        
        On the first bar, creates grid levels below the initial price.
        On subsequent bars, checks if price has reached any grid level
        and executes buy orders with take-profit targets.
        """
        # On first bar: establish initial price and create grid levels
        if self.initial_price is None:
            self.initial_price = self.data.Close[-1]
            
            # Create grid levels below initial price
            # Each level is grid_profit % below the previous level
            for i in range(1, self.grid_buy + 1):
                level = self.initial_price * (1 - (i * self.grid_profit / 100))
                self.grid_levels.append(level)
        
        current_price = self.data.Close[-1]
        
        # Check if price has reached any grid level
        for level in self.grid_levels:
            # Buy at grid level if price drops to or below it
            if current_price <= level and not self.position:
                # Calculate take-profit target (grid_profit % above entry)
                target_price = level * (1 + self.grid_profit / 100)
                # Execute buy order with take-profit
                self.buy(tp=target_price)
                break  # Only one grid level per bar
