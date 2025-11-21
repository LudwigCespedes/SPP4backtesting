"""
Configuración de símbolos y parámetros por defecto para backtesting.
"""

import datetime as dt

# Símbolos de criptomonedas
CRYPTO_SYMBOLS = {
    'BTC': 'BTC-USD',
    'ETH': 'ETH-USD',
    'BNB': 'BNB-USD',
    'DOT': 'DOT-USD',
    'CAKE': 'CAKE-USD',
    'XAU': 'XAUT-USD',  # Gold token
}

# Símbolos de acciones
STOCK_SYMBOLS = {
    'COIN': 'COIN',
    'NVDA': 'NVDA',
    'AAPL': 'AAPL',
}

# Fechas por defecto
DEFAULT_START_DATE = dt.datetime(2015, 1, 1)
DEFAULT_END_DATE = dt.datetime.now()

# Parámetros de backtesting por defecto
DEFAULT_CASH = 10  # En millones (10M)
DEFAULT_COMMISSION = 0.01  # 1%

# Configuración de optimización
DEFAULT_WALK_FORWARD_PERIOD = 365  # días
DEFAULT_MAXIMIZE_METRIC = 'Sortino Ratio'

# Métricas para graficar
DEFAULT_PLOT_METRICS = [
    'Alpha [%]',
    'Win Rate [%]',
    'Kelly Criterion',
    'Sortino Ratio'
]
