# SPP4backtesting

Sistema de backtesting para estrategias de trading en criptomonedas y acciones, utilizando la librería `backtesting.py` con datos de `yfinance`.

## 📋 Características

- **Estructura Modular**: Código organizado en módulos reutilizables
- **Múltiples Estrategias**: 11+ estrategias pre-implementadas (MACD, SMA, Momentum, etc.)
- **Optimización Walk-Forward**: Validación robusta de estrategias
- **Gestión de Datos**: Carga y caché automático de datos históricos
- **Visualización**: Gráficos interactivos y reportes HTML
- **Fácil Extensión**: Clase base para crear nuevas estrategias

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio** (si aplica):
   ```bash
   git clone <url-del-repositorio>
   cd SPP4backtesting
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar instalación**:
   ```bash
   python -c "import backtesting; import yfinance; import talib; print('OK')"
   ```

## 📁 Estructura del Proyecto

```
SPP4backtesting/
├── src/                      # Código fuente principal
│   ├── strategies/          # Estrategias de trading
│   │   ├── base.py         # Clase base
│   │   ├── macd_strategies.py
│   │   ├── sma_strategies.py
│   │   ├── momentum_strategies.py
│   │   ├── grid_strategies.py
│   │   └── arbitrage_strategies.py
│   ├── utils/              # Utilidades
│   │   ├── data_loader.py  # Carga de datos
│   │   ├── optimization.py # Optimización
│   │   └── plotting.py     # Visualización
│   └── config/             # Configuraciones
│       └── symbols.py      # Símbolos y parámetros
├── scripts/                # Scripts ejecutables
│   ├── run_macd_adx_ema.py
│   ├── run_sma_strategy.py
│   └── run_optimization.py
├── data/                   # Datos históricos
│   ├── raw/               # Datos descargados
│   └── processed/         # Datos procesados
├── results/               # Resultados de backtests
│   ├── html/             # Reportes HTML
│   ├── csv/              # Resultados CSV
│   └── plots/            # Gráficos PNG
├── notebooks/            # Jupyter notebooks
├── tests/                # Tests unitarios
├── legacy/               # Scripts antiguos (deprecated)
├── README.md
└── requirements.txt
```

## 🎯 Uso Rápido

### Ejemplo 1: Backtest Simple

```python
from src.strategies.sma_strategies import BTSMAStrategy
from src.utils.data_loader import load_crypto_data
from backtesting import Backtest

# Cargar datos
data = load_crypto_data('BTC-USD', period='1y', normalize=True)

# Ejecutar backtest
bt = Backtest(data, BTSMAStrategy, cash=10, commission=0.01)
stats = bt.run()

# Mostrar resultados
print(stats)
bt.plot()
```

### Ejemplo 2: Optimización Walk-Forward

```python
from src.strategies.macd_strategies import MacdAdxEmaStrategy
from src.utils.data_loader import load_crypto_data
from src.utils.optimization import walk_forward
from src.utils.plotting import plot_stats

# Cargar datos
data = load_crypto_data('BTC-USD', period='max', normalize=True)

# Optimización walk-forward
stats = walk_forward(
    data,
    MacdAdxEmaStrategy,
    maximize='Sortino Ratio',
    constraint=lambda p: p.macdfast < p.macdslow
)

# Visualizar resultados
plot_stats(stats, strategy_name="MacdAdxEma")
```

### Ejemplo 3: Usar Scripts Predefinidos

```bash
# Ejecutar estrategia MACD + ADX + EMA con optimización
python scripts/run_macd_adx_ema.py

# Ejecutar estrategia SMA simple
python scripts/run_sma_strategy.py

# Comparar múltiples estrategias
python scripts/run_optimization.py
```

## 📊 Estrategias Disponibles

### Estrategias MACD
- **MacdAdxEmaStrategy**: MACD + ADX + EMA para filtrado de tendencias
- **MacdAdxStrategy**: MACD + ADX simplificado
- **MacdStrategy**: MACD puro
- **MacdAdxSmaStrategy**: MACD + ADX + SMA

### Estrategias SMA
- **BTSMAStrategy**: Cruce de SMAs con SL/TP dinámicos
- **SmaAdxStrategy**: SMA + ADX para filtrado

### Estrategias de Momentum
- **MomentumStrategy**: Basada en indicador de Momentum
- **KamaStrategy**: Kaufman Adaptive Moving Average
- **LinearRegressionStrategy**: Regresión lineal

### Estrategias de Grid Trading
- **GridStrategy**: Grid trading con niveles de precio predefinidos

### Estrategias de Arbitraje
- **UsdtUsdcArbitrage**: Arbitraje entre stablecoins USDT/USDC

## 🛠️ Crear Tu Propia Estrategia

```python
from src.strategies.base import BaseStrategy
from backtesting.lib import crossover
import talib

class MiEstrategia(BaseStrategy):
    # Parámetros
    periodo = 20
    
    # Rangos para optimización
    opt_ranges = {
        'periodo': range(10, 50, 5)
    }
    
    def init(self):
        """Inicializar indicadores."""
        self.sma = self.I(talib.SMA, self.data.Close, self.periodo)
    
    def next(self):
        """Lógica de trading."""
        if crossover(self.data.Close, self.sma):
            self.buy()
        elif crossover(self.sma, self.data.Close):
            self.position.close()
```

## 📈 Métricas de Evaluación

Las estrategias se evalúan usando:

- **Return [%]**: Retorno total
- **Sharpe Ratio**: Retorno ajustado por riesgo
- **Sortino Ratio**: Similar a Sharpe pero solo considera volatilidad negativa
- **Max. Drawdown [%]**: Máxima caída desde un pico
- **Win Rate [%]**: Porcentaje de operaciones ganadoras
- **Alpha [%]**: Retorno en exceso sobre el benchmark
- **Kelly Criterion**: Tamaño óptimo de posición

## 🔧 Configuración

Edita `src/config/symbols.py` para personalizar:

- Símbolos de criptomonedas y acciones
- Fechas por defecto
- Capital inicial y comisiones
- Métricas a graficar

## 📝 Notas Importantes

1. **Normalización de Precios**: Los datos se dividen por 10^6 para facilitar el backtesting con capital en millones
2. **Multiprocessing**: La optimización usa múltiples cores para acelerar el proceso
3. **Caché de Datos**: Los datos descargados se pueden cachear en `data/raw/`
4. **Scripts Legacy**: Los scripts originales están en `legacy/` como referencia

## 🤝 Contribuir

Para agregar nuevas estrategias:

1. Crea una nueva clase en el módulo apropiado de `src/strategies/`
2. Hereda de `BaseStrategy` o `Strategy`
3. Define `opt_ranges` para optimización
4. Implementa `init()` y `next()`
5. Agrega la estrategia al `__init__.py` del módulo

## 📄 Licencia

Este proyecto es de uso personal y educativo.

## 👤 Autor

Ludwig Cespedes

## 🙏 Agradecimientos

- [backtesting.py](https://kernc.github.io/backtesting.py/) - Framework de backtesting
- [yfinance](https://github.com/ranaroussi/yfinance) - Descarga de datos
- [TA-Lib](https://ta-lib.org/) - Indicadores técnicos
