from backtesting import Backtest
import pandas as pd
def walk_forward1(
        strategy,
        data_full,
        warmup_bars,
        lookback_bars,
        validation_bars,
        cash = 10,
        commision = 0.01
    ):
    stats_master = []
    for i in range(lookback_bars,len(data_full)-validation_bars,validation_bars):
        training_data = data_full.iloc[i-lookback_bars - warmup_bars:i]
        validation_bars = data_full.iloc[i-warmup_bars:i+validation_bars]
        bt_training =  Backtest(training_data,strategy, cash=cash, commission=commision)
        stats_training = bt_training.optimize(n1 =range(1,20),
                n2 = range(1,20), 
                maximize='Alpha [%]')
        small_threshold = stats_training.__strategy.n1
        large_threshold = stats_training.__strategy.n2
        bt_validation =  Backtest(validation_bars,strategy, cash=cash, commission=commision)
        stats_validation = bt_validation.run(n1= small_threshold,n2 = large_threshold)

        stats_master.append(stats_validation)
    return stats_master    

def walk_forward(data):
    train = data[len(data)*0.5]
    return train
    
pd.re    
    
#stats = bt.run()
