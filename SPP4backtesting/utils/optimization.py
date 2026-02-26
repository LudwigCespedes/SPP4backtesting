from backtesting import Backtest
from backtesting.lib import FractionalBacktest
import pandas as pd
from typing import Callable, Optional, Dict, List, Any

def walk_forward(data:pd.DataFrame,
                 strategy,cash,commission,maximize:str = 'Sortino Ratio',constraint = lambda p: p.n1< p.n2 ):
    
    stats_master = []
    size_optimization = 1095
    size_test = int(size_optimization * 0.35)
    
    df = data.iloc[size_optimization+size_test:]
    train = data.iloc[:size_optimization]
    test = data.iloc[size_optimization:size_optimization+size_test]
    
    brocks = [df.iloc[i:i+size_test] for i in range(size_optimization,len(data),size_test) if i < len(df)]
    
    bt = FractionalBacktest(train,strategy=strategy,cash=cash)
    stats = optimize_auto(bt, strategy, maximize, constraint)
    
    bt = FractionalBacktest(test, strategy, cash=cash, commission=commission)
    stats = bt.run(**stats._strategy._params)
    stats_master.append(stats)

    for i in range(len(brocks)):
    
        bt = FractionalBacktest(brocks[i], strategy, cash=cash, commission=commission)
        stats = optimize_auto(bt, strategy, maximize, constraint)
        if i+1<len(brocks):
            bt = FractionalBacktest(brocks[i+1], strategy, cash=cash, commission=commission)
            stats = bt.run(**stats._strategy._params)
            stats_master.append(stats)
    
    return stats_master

        
    

def _walk_forward(
    data: pd.DataFrame,
    strategy,
    depp: int = 365,
    maximize: str = 'Sortino Ratio',
    cash: float = 100,
    commission: float = 0.01,
    constraint: Optional[Callable] = None
) -> List[Any]:

    test = data.iloc[len(data)//4:int((len(data)//2))]
    
    stats_master = []

    
    bt = Backtest(train, strategy, cash=cash, commission=commission)
    stats = optimize_auto(bt, strategy, maximize, constraint)
    
    
    bt = Backtest(test, strategy, cash=cash, commission=commission)
    stats = bt.run(**stats._strategy._params)
    stats_master.append(stats)
    
    # Walk-forward loop
    for i in range(len(data)//2, len(data), depp):
        train = pd.concat([train[len(train)//2:], test])
        train = train[~train.index.duplicated(keep="first")].sort_index()

        test = pd.concat([test[len(test)//2:], data.iloc[i-depp:i+depp]])
        test = test[~test.index.duplicated(keep="first")].sort_index()

        bt = Backtest(train, strategy, cash=cash, commission=commission)
        stats = optimize_auto(bt, strategy, maximize, constraint)
        
        bt = Backtest(test, strategy, cash=cash, commission=commission)
        stats = bt.run(**stats._strategy._params)
        stats_master.append(stats)
    
    return stats_master


def optimize_auto(
    bt: Backtest,
    StrategyCls,
    maximize: str = 'Sortino Ratio',
    constraint: Optional[Callable] = None
):

    ranges = getattr(StrategyCls, 'opt_ranges', None)
    if not ranges:
        raise ValueError(
            f"{StrategyCls.__name__}"
        )
    
    return bt.optimize(**ranges, maximize=maximize, constraint=constraint) 
