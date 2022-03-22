from .Base_Grid import Base_Grid
import matplotlib.pyplot as plt
import math

class Selling_Grid(Base_Grid):
    
    def __init__(self, df, investment, minutes, orders, spread, ticker, market_sell=True, only_above=True,
                 period=1000, grid_type='static'):
        
        super().__init__(df, investment, minutes, orders, spread, period, ticker, grid_type)
        
        self.grid_type = grid_type
        self.market_sell = market_sell
        self.only_above = only_above
        
        if grid_type == 'static':
            self.static_sell_list()
            self.start_sell_list = self.static_sell_list()

        self.set_start_quantities()
        
    def try_market_sale(self):
        if self.market_sell == True:
            if self.usdt == 0 and self.current_minute == 0:
                self.execute_sale(self.current_price)
                self.tq_per_order = float(self.tq/self.orders)
                if self.only_above == True:
                    self.tq_per_order *= 2
                
    def set_start_quantities(self):
        if self.only_above == True:
            self.tq_per_order *= 2
        self.try_market_sale()
            
    def round_number(self, num):
        num=f"{float(num):.9f}"
        if '.' in num:
            decimal_index = num.index('.')
            round_decimals = 7 - decimal_index
            if round_decimals < 0:
                round_decimals = 0
            if num[decimal_index-1] == '0':
                round_decimals += 3
            num=num.rstrip('0')
            num = round(float(num), round_decimals)
        else:
            print("No '.' value in string number.")
        return num
    
    def execute_sale(self, sale_price=0):
        if sale_price == 0:
            sale_price = self.sell_list[0]
        print('{ticker} quantity: {quantity}'.format(ticker=self.ticker, quantity=self.tq))
        print('{ticker} per order quantity: {per_order}'.format(ticker=self.ticker, per_order=self.tq_per_order))
        if self.tq > self.tq_per_order and self.current_price >= sale_price:
            print('Executing sale at price: {} current price is: {}'.format(sale_price, 
                                                                       self.current_price))
            self.tq -= self.tq_per_order
            self.usdt += (self.tq_per_order * sale_price * 0.9992)
            self.sell_trans[self.current_minute] = sale_price
            self.index_sell_trans[self.series.index[self.current_minute]] = sale_price
            self.last = float(sale_price)
        else:
            print('Error! Not enough {} to execute order.'.format(self.ticker))
            
    def increment_minute(self):
        if self.grid_type == 'static':
            self.static_sell_list()
        else:
            self.downfill_sell_list()
        self.current_minute += 1
        if self.current_minute < len(self.series):
            self.current_price = self.series.iloc[self.current_minute]
        else:
            print('Selling grid finished incrementing.')
        
    def static_sell_list(self):
        if self.only_above:
            self.sell_list = [x for x in self.order_list if float(x) > float(self.start_price) and x not in self.sell_trans.values()]
        else:
            self.sell_list = [x for x in self.order_list if float(x) > float(self.current_price) and x not in 
                              self.sell_trans.values()]
        return self.sell_list
            
    def graph(self):
        plt.clf()
        plt.plot(self.series)
        plt.plot([self.series.index[0] for x in range(len(self.start_sell_list))], self.start_sell_list, 'h', color='red')
        plt.plot(self.index_sell_trans.keys(), self.sell_trans.values(), 'h', color='red')
        
    def store_debt(self):
        self.debt_list.append(self.current_price * (self.start_tq - self.tq))
        self.current_debt = self.current_price * (self.start_tq - self.tq)
        
    def execute_current_minute(self):
        if self.current_minute == len(self.series)-1:
            self.debt = (self.start_tq - (len(self.sell_trans) * self.tq_per_order)) * self.finish_price
        if self.current_minute < len(self.series):
            if float(self.tq_per_order) < float(self.tq) and len(self.sell_list) > 0:
                if self.current_price > self.sell_list[0]:
                    self.execute_sale()
                else:
                    self.try_market_sale()
            self.store_debt()
            self.increment_minute()
        else:
            print('Minute {} out of {}, finished incrementing through data.'.format(self.current_minute, len(self.series)))
            
    def run_simulation(self):
        print('Starting simulation...')
        while self.current_minute < len(self.series)-1:
            if float(self.tq_per_order) < float(self.tq):
                if self.current_price > self.sell_list[0]:
                    self.execute_sale()
            self.increment_minute()
        
        if len(self.sell_trans.values()) == 0:
            print("No transactions.")
        else:
            print(
                """
                Grid Finished at {} minutes.
                finish_price: {}
                past_transactions: {}
                average_sell_price: {}
                Total BTC Sold: {}
                Total USD Obtained: {}
            """.format(self.current_minute, self.current_price, self.sell_trans,
                       sum(self.sell_trans.values())/len(self.sell_trans.values()), self.tq_per_order*len(self.sell_trans),
                      self.usdt))
