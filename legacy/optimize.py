from backtesting import Backtest
import pandas as pd
import matplotlib.pyplot as plt
import time
def plot_stats(stats,paranm_to_plot=['Alpha [%]','Win Rate [%]','Kelly Criterion','Sortino Ratio']):
    #fig, ax = plt.subplots(figsize=(5, 3), layout='constrained')
    stats_df= pd.DataFrame(stats)

    #for stat in  stats:
    #equity_curve = getattr(stats,paranm_to_plot).dropna()
    #x = equity_curve.index
    #print(x)
    #ax.plot(equity_curve)
    #plt.plot(equity_curve[0],equity_curve[1])
    #equity_curve.plot(subplots = True)
    
    stats_df.loc[:,paranm_to_plot].plot(kind="bar",subplots=True,figsize=(10,10),grid=True)
    #print(stats_df[:,paranm_to_plot].max())
    stats_df.to_csv(f'data/{time.ctime()}.csv')
    plt.savefig(f'data/{time.ctime()}.png')
    plt.show()

    #bt=Backtest(aligned_data,strategy,cash = 10,commission = 0.02)


def walk_forward(data, strategy, depp=365, maximize = 'Sortino Ratio',cash=100, commission=.01,constraint = None):
    train = data.iloc[:len(data)//4]
    test  = data.iloc[len(data)//4:int((len(data)//2))]
    
    stats_master = []

    # Optimización inicial en train
    bt = Backtest(train, strategy, cash=cash, commission=commission)
    stats = optimize_auto(bt, strategy, maximize,constraint)
    
    # Evaluación inicial en test
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
        stats = optimize_auto(bt, strategy, maximize,constraint)
        
        bt = Backtest(test, strategy, cash=cash, commission=commission)
        stats = bt.run(**stats._strategy._params)
        stats_master.append(stats)
    
    return stats_master

def optimize_auto(bt: Backtest, StrategyCls, maximize='Sortino Ratio',
                  constraint=None):
    ranges = getattr(StrategyCls, 'opt_ranges', None)
    if not ranges:
        raise ValueError("Define 'opt_ranges' en tu Strategy (dict de iterables).")
    
    return bt.optimize(**ranges, maximize=maximize, constraint=constraint) 
    
#stats = bt.run()
