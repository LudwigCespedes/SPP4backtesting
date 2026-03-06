import pandas as pd
from backtesting import Backtest
from backtesting.lib import FractionalBacktest

class WalkForward:
    def __init__(self,data:pd.DataFrame,
                 strategy,cash,commission,maximize:str = 'Sortino Ratio',
                 constraint = lambda p: p.n1< p.n2 ):
        self.data=data
        self.strategy = strategy
        self.cash = cash
        self.commission = commission
        self.maximize = maximize
        self.constraint = constraint
        #5*365
        self.size_optimization = 3*365
        self.size_test = int(self.size_optimization * 0.35)
        
        self.stats_master = []
        self.stats_train = []
        self.stats_test = []
    
        self.Backtest = Backtest
        self.FractionalBacktest = FractionalBacktest
        self.train = self.data.iloc[:self.size_optimization]
        self.test = self.data.iloc[self.size_optimization:self.size_optimization+self.size_test]
        self.out_of_sample_data = self.data.iloc[self.size_optimization+self.size_test:]
        self.walk = [self.out_of_sample_data[i:i+self.size_test] for i in range(self.size_optimization,len(self.out_of_sample_data),self.size_test) if i < len(self.out_of_sample_data)]
        
    def optimize_auto(self,bt,strategy,maximize: str = 'Sortino Ratio', constraint = lambda p: p.n1< p.n2):

        ranges = getattr(strategy, 'opt_ranges', None)
        if not ranges:
            raise ValueError(
                f"{StrategyCls.__name__}"
            )
        
        return bt.optimize(**ranges, maximize=maximize, constraint=constraint) 
        
        
    def run_walk_forward(self):
    
    
        bt = self.FractionalBacktest(self.train,self.strategy,cash=self.cash,commission=self.commission,finalize_trades=True)
        self.stats_train = self.optimize_auto(bt, self.strategy, self.maximize, self.constraint)
        
        bt = self.FractionalBacktest(self.test,self.strategy,cash=self.cash,commission=self.commission,finalize_trades=True)
        self.stats_test = bt.run(**self.stats_train._strategy._params)
        
        self.stats_master.append([self.stats_train,self.stats_test])

        for i in range(len(self.walk)):
            
            bt = self.FractionalBacktest(self.walk[i], self.strategy, cash=self.cash, commission=self.commission,finalize_trades=True)
            self.stats_train = self.optimize_auto(bt, self.strategy, self.maximize, self.constraint)
            
            if i+1<len(self.walk):
            
                bt = self.FractionalBacktest(self.walk[i+1], self.strategy, cash=self.cash, commission=self.commission,finalize_trades=True)
                
                self.stats_test = bt.run(**self.stats_train._strategy._params)
                self.stats_master.append([self.stats_train,self.stats_test])
        
        return self.stats_master

