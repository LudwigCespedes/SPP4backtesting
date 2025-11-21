# Scripts Legacy (Deprecated)

Esta carpeta contiene los scripts originales del proyecto antes de la restructuración.

## ⚠️ Advertencia

Estos scripts están aquí solo como referencia y **no deben ser usados** en producción. Usa los nuevos módulos en `src/` y scripts en `scripts/` en su lugar.

## Migración

Todos los scripts han sido migrados a la nueva estructura:

### Estrategias MACD
- `bt_macd_adx_ema.py` → `src/strategies/macd_strategies.py::MacdAdxEmaStrategy`
- `bt_macd_adx.py` → `src/strategies/macd_strategies.py::MacdAdxStrategy`
- `btmacd.py` → `src/strategies/macd_strategies.py::MacdStrategy`
- `btmacd_adx.py` → `src/strategies/macd_strategies.py::MacdAdxSmaStrategy`

### Estrategias SMA
- `btsma.py` → `src/strategies/sma_strategies.py::BTSMAStrategy`
- `bt_sma_adx.py` → `src/strategies/sma_strategies.py::SmaAdxStrategy`

### Estrategias de Momentum
- `bt_mom.py` → `src/strategies/momentum_strategies.py::MomentumStrategy`
- `bt_kama.py` → `src/strategies/momentum_strategies.py::KamaStrategy`
- `bt_linear_regression.py` → `src/strategies/momentum_strategies.py::LinearRegressionStrategy`

### Estrategias de Grid Trading
- `bt_grid.py` → `src/strategies/grid_strategies.py::GridStrategy`

### Estrategias de Arbitraje
- `btusdt-usdc.py` → `src/strategies/arbitrage_strategies.py::UsdtUsdcArbitrage`

### Utilidades
- `optimize.py` → `src/utils/optimization.py` y `src/utils/plotting.py`

## Cómo Usar la Nueva Estructura

En lugar de:
```python
from optimize import walk_forward, plot_stats
```

Usa:
```python
from src.utils.optimization import walk_forward
from src.utils.plotting import plot_stats
```

Para más información, consulta el `README.md` principal del proyecto.
