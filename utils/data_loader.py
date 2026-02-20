"""
Módulo para carga y gestión de datos de mercado.

Este módulo proporciona funciones para descargar datos históricos de precios
desde yfinance y prepararlos para backtesting.
"""

import yfinance as yf
import datetime as dt
import pandas as pd
from typing import Optional, Union, List, Dict
import os


def load_crypto_data(
    symbol: str,
    start: Optional[dt.datetime] = None,
    end: Optional[dt.datetime] = None,
    interval: str = "1d",
    period: Optional[str] = None,
    normalize: bool = True
) -> pd.DataFrame:
    """
    Carga datos históricos de una criptomoneda.
    
    Args:
        symbol: Símbolo de la criptomoneda (ej: 'BTC-USD')
        start: Fecha de inicio (opcional si se usa period)
        end: Fecha de fin (opcional si se usa period)
        interval: Intervalo de tiempo ('1d', '1h', '5m', etc.)
        period: Período de tiempo ('1mo', '1y', 'max', etc.)
        normalize: Si True, divide los precios por 10^6
        
    Returns:
        DataFrame con datos OHLCV
    """
    ticker = yf.Ticker(symbol)
    
    if period:
        data = ticker.history(period=period, interval=interval)
    else:
        if start is None:
            start = dt.datetime(2015, 1, 1)
        if end is None:
            end = dt.datetime.now()
        data = ticker.history(start=start, end=end, interval=interval)
    
    # Seleccionar solo columnas OHLCV
    data = data.iloc[:, :4]  # Open, High, Low, Close
    
    # Normalizar precios si es necesario
    if normalize:
        data = data * 10**-6
    
    return data


def load_stock_data(
    symbol: str,
    start: Optional[dt.datetime] = None,
    end: Optional[dt.datetime] = None,
    interval: str = "1d",
    period: Optional[str] = None,
    normalize: bool = True
) -> pd.DataFrame:
    """
    Carga datos históricos de una acción.
    
    Args:
        symbol: Símbolo de la acción (ej: 'AAPL', 'NVDA')
        start: Fecha de inicio
        end: Fecha de fin
        interval: Intervalo de tiempo
        period: Período de tiempo
        normalize: Si True, divide los precios por 10^6
        
    Returns:
        DataFrame con datos OHLCV
    """
    return load_crypto_data(symbol, start, end, interval, period, normalize)


def load_multiple_symbols(
    symbols: List[str],
    start: Optional[dt.datetime] = None,
    end: Optional[dt.datetime] = None,
    interval: str = "1d",
    normalize: bool = True
) -> Dict[str, pd.DataFrame]:
    """
    Carga datos históricos de múltiples símbolos.
    
    Args:
        symbols: Lista de símbolos a cargar
        start: Fecha de inicio
        end: Fecha de fin
        interval: Intervalo de tiempo
        normalize: Si True, divide los precios por 10^6
        
    Returns:
        Diccionario con símbolo como clave y DataFrame como valor
    """
    data_dict = {}
    
    for symbol in symbols:
        print(f"Cargando datos para {symbol}...")
        try:
            data = load_crypto_data(
                symbol=symbol,
                start=start,
                end=end,
                interval=interval,
                normalize=normalize
            )
            data_dict[symbol] = data
        except Exception as e:
            print(f"Error cargando {symbol}: {e}")
    
    return data_dict


def save_data_cache(
    data: pd.DataFrame,
    symbol: str,
    cache_dir: str = "data/raw"
) -> None:
    """
    Guarda datos en caché para evitar descargas repetidas.
    
    Args:
        data: DataFrame con los datos
        symbol: Símbolo del activo
        cache_dir: Directorio donde guardar el caché
    """
    os.makedirs(cache_dir, exist_ok=True)
    filepath = os.path.join(cache_dir, f"{symbol}.csv")
    data.to_csv(filepath)
    print(f"Datos guardados en {filepath}")


def load_data_cache(
    symbol: str,
    cache_dir: str = "data/raw"
) -> Optional[pd.DataFrame]:
    """
    Carga datos desde caché si existen.
    
    Args:
        symbol: Símbolo del activo
        cache_dir: Directorio donde buscar el caché
        
    Returns:
        DataFrame con los datos o None si no existe
    """
    filepath = os.path.join(cache_dir, f"{symbol}.csv")
    
    if os.path.exists(filepath):
        print(f"Cargando datos desde caché: {filepath}")
        return pd.read_csv(filepath, index_col=0, parse_dates=True)
    
    return None


def load_multimarket_data(
    start: Optional[dt.datetime] = None,
    end: Optional[dt.datetime] = None,
    interval: str = "1d",
    period_days: Optional[int] = None,
    normalize: bool = True,
    symbols: Optional[Dict[str, List[str]]] = None
) -> tuple[Dict[str, pd.DataFrame], List[str]]:
    """
    Carga datos históricos para múltiples mercados de forma eficiente.
    
    Esta función facilita la carga de datos para pruebas multimercado,
    organizando los activos por categorías (Cripto, Índices, Forex, Commodities).
    
    Args:
        start: Fecha de inicio (opcional si se usa period_days)
        end: Fecha de fin (opcional, por defecto datetime.now())
        interval: Intervalo de tiempo ('1d', '1h', '5m', etc.)
        period_days: Número de días hacia atrás desde hoy (alternativa a start/end)
        normalize: Si True, divide los precios por 10^6
        symbols: Diccionario personalizado de símbolos por categoría.
                 Si es None, usa configuración por defecto.
                 Formato: {'categoria': ['SYMBOL1', 'SYMBOL2', ...]}
    
    Returns:
        Tupla con:
        - Diccionario con datos {símbolo: DataFrame}
        - Lista con nombres de símbolos en orden
    
    Example:
        >>> # Cargar datos de los últimos 60 días con intervalo de 1 hora
        >>> data, symbols = load_multimarket_data(
        ...     period_days=60,
        ...     interval='1h'
        ... )
        >>> 
        >>> # Cargar datos personalizados
        >>> custom_symbols = {
        ...     'Cripto': ['BTC-USD', 'ETH-USD'],
        ...     'Indices': ['^GSPC']
        ... }
        >>> data, symbols = load_multimarket_data(
        ...     start=dt.datetime(2020, 1, 1),
        ...     symbols=custom_symbols
        ... )
    """
    # Configuración por defecto de símbolos
    if symbols is None:
        symbols = {
            'Cripto': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'DOT-USD', 'CAKE-USD'],
            'Indices': ['^GSPC'],  # S&P 500
            'Forex': ['EURUSD=X'],
            'Commodities': ['GC=F']  # Gold Futures
        }
    
    # Determinar fechas
    if period_days is not None:
        end = dt.datetime.now()
        start = end - dt.timedelta(days=period_days)
    else:
        if start is None:
            start = dt.datetime(2015, 1, 1)
        if end is None:
            end = dt.datetime.now()
    
    # Crear lista plana de todos los símbolos
    all_symbols = []
    for category, symbol_list in symbols.items():
        all_symbols.extend(symbol_list)
    
    # Cargar datos para todos los símbolos
    print(f"📥 Cargando datos de {len(all_symbols)} activos...")
    print(f"📅 Período: {start.date()} a {end.date()}")
    print(f"⏱️  Intervalo: {interval}\n")
    
    data_dict = {}
    failed_symbols = []
    
    for i, symbol in enumerate(all_symbols, 1):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start, end=end, interval=interval)
            
            if data.empty:
                print(f"⚠️  [{i}/{len(all_symbols)}] {symbol}: Sin datos disponibles")
                failed_symbols.append(symbol)
                continue
            
            # Seleccionar solo columnas OHLCV
            data = data.iloc[:, :4]
            
            # Normalizar si es necesario
            if normalize:
                data = data * 10**-6
            
            data_dict[symbol] = data
            print(f"✅ [{i}/{len(all_symbols)}] {symbol}: {len(data)} registros")
            
        except Exception as e:
            print(f"❌ [{i}/{len(all_symbols)}] {symbol}: Error - {str(e)}")
            failed_symbols.append(symbol)
    
    # Resumen
    print(f"\n{'='*60}")
    print(f"✅ Descargados: {len(data_dict)}/{len(all_symbols)} activos")
    if failed_symbols:
        print(f"❌ Fallidos: {', '.join(failed_symbols)}")
    print(f"{'='*60}\n")
    
    # Retornar solo símbolos exitosos
    successful_symbols = [s for s in all_symbols if s in data_dict]
    
    return data_dict, successful_symbols
