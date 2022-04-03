from .Base_Grid import Base_Grid
import pandas as pd

class Smart_Grid(Base_Grid):
    def __init__(self, selling_grid, df, ticker, orders, spread, investment, minutes,
                 update_frequency=100, period=3000, grid_type='dynamic', ma_ind=True, fill_bot=True, repeat_buys=False,
                repeat_sells=False, base='BTC'):
        
        self.grid_type = grid_type
        self.ma_ind = ma_ind
        self.fill_bot = fill_bot
        self.repeat_buys = repeat_buys
        self.repeat_sells = repeat_sells
        self.selling_grid = selling_grid
        
        super().__init__(df, investment, minutes, orders, spread, period, ticker, grid_type, base=base)
        
        self.sell_ticker = selling_grid.ticker
        self.update_frequency = update_frequency
        self.selling_start_tq = selling_grid.start_tq
        
        self.fast_ma = self.entire_series.rolling(100).mean().dropna()
        if len(self.series) < len(self.ma):
            self.ma = self.ma.iloc[-len(self.series):]
        if len(self.series) < len(self.fast_ma):
            self.fast_ma = self.fast_ma.iloc[-len(self.series):]
            
        self.diff = (self.ma - self.fast_ma).dropna()
        self.dstd = (self.diff.rolling(period).std()).dropna()
        self.get_stop_line()
        
        self.usdt = self.selling_grid.usdt
        self.selling_grid.usdt = 0
        self.current_minute = selling_grid.current_minute
        self.current_price = self.series.iloc[self.current_minute]
        self.tq = 0
        self.tq_per_order = float(self.investment/self.start_price)/self.orders
        self.finish_price = self.series.iloc[-1]
        
        self.update_lists()
        self.start_buy_list, self.start_sell_list = self.buy_list, self.sell_list
        
    def update_order_list(self):
        if self.current_price > max(self.order_list) or self.current_price < min(self.order_list) and self.grid_type == 'dynamic':
            self.order_list = [self.round_number(((1-self.spread/200)+x*self.spread/self.orders/100) * self.current_price) 
                   for x in range(self.orders+1)]
        self.update_lists()
        
    def filter_buy_list(self):
        if self.current_index in self.stop_line.index:
            if str(self.stop_line[self.current_index]) == 'nan':
                self.buy_list = []
                self.sell_list = []
            elif self.buy_list == []:
                self.update_lists()
        if self.repeat_sells == False:
            if self.consecutive_type == 'sell':
                self.sell_list = [x for x in self.sell_list if float(x) not in self.consecutive_trans.values()]
        if self.repeat_buys == False:
            if self.consecutive_type == 'buy':
                self.buy_list = [x for x in self.buy_list if float(x) not in self.consecutive_trans.values()]
        
    def get_stop_line(self):
        stop_line = {}
        for count, val in self.dstd.items():
            if self.diff[count] < val and self.diff[count] > -val:
                stop_line[count] = val
            else:
                stop_line[count] = None
        if len(self.df) > self.minutes+self.period+1:
            self.stop_line = pd.Series(stop_line)
        else:
            self.stop_line = pd.Series(stop_line)
                
    def get_buy_list(self):
        if self.grid_type == 'static' and self.ma_ind==False:
            buy_list = [x for x in self.order_list if float(x) < float(self.start_price) 
                        and float(x) != self.last and float(x) < self.current_price]
            
        elif self.grid_type=='static' and self.ma_ind==True and int(self.current_index) in self.ma.index:
            buy_list = [x for x in self.order_list if float(x) < float(self.ma.loc[self.current_index]) and float(x) != self.last
                        and float(x) < self.current_price and float(x) < self.start_price]
            
        elif self.ma_ind == True and self.current_minute >= self.period and self.minutes+self.period >= len(self.entire_series):
            buy_list = [x for x in self.order_list if float(x) < float(self.current_price) and float(x) != float(self.last)
                       and float(x) < float(self.ma.loc[self.current_index])]
            
        elif self.ma_ind == True and self.minutes+self.period < len(self.entire_series) and self.current_index in self.ma.index:
            buy_list = [x for x in self.order_list if float(x) < float(self.current_price) and float(x) != float(self.last)
                       and float(x) < float(self.ma.loc[self.current_index])]
        else:
            # print('minute: {} self.current_price: {}'.format(self.current_minute, self.current_price))
            buy_list = [x for x in self.order_list if float(x) < float(self.current_price) and float(x) != float(self.last)]
        self.buy_list = buy_list
        
    def get_sell_list(self):
        if self.grid_type=='static' and self.ma_ind==False:
            # Only sell above start price.
            sell_list = [x for x in self.order_list if float(x) > float(self.start_price) and float(x) != self.last
                        and float(x) > self.current_price]
        elif self.grid_type=='static' and self.ma_ind==True and int(self.current_index) in self.ma.index:
            # Only sell above start price AND above MA.
            sell_list = [x for x in self.order_list if float(x) > float(self.ma.loc[self.current_index]) and float(x) != self.last
                        and float(x) > self.current_price and float(x) > self.start_price]
        elif self.ma_ind == True and self.current_minute >= self.period and self.minutes+self.period >= len(self.entire_series):
            # Only sell above MA IF MA exists and current MA index is not greater than the entire series.
            sell_list = [x for x in self.order_list if float(x) > float(self.current_price) and float(x) != float(self.last)
                        and float(x) > self.ma.loc[self.current_index]]
        elif self.ma_ind == True and self.minutes+self.period < len(self.entire_series):
            # Only sell above MA IF MA exists and the MA line is less than the entire series.
            sell_list = [x for x in self.order_list if float(x) > float(self.current_price) and float(x) != float(self.last)
                        and float(x) > self.ma.loc[self.current_index]]
        else:
            sell_list = [x for x in self.order_list if float(x) > float(self.current_price) and float(x) != float(self.last)]
        self.sell_list = sell_list
        
    def update_lists(self):
        self.get_buy_list()
        self.get_sell_list()
        
    def get_current_value(self):
        assets = self.usdt + (self.tq * self.current_price)
        self.current_assets.append(assets)
        self.current_value.append(assets - self.selling_grid.current_debt)
        
    def try_execute_purchase(self):
        if len(self.buy_list) > 0:
            purchase_price = float(self.buy_list[-1])
            if float(self.usdt) > float(self.tq_per_order * purchase_price) and float(self.current_price) < purchase_price and purchase_price not in self.recent_buys.values():
                # print('Executing purchase at: {}, current price is lesser at: {}, last: {}, minute: {}'.format(purchase_price, self.current_price,
                                                                                                #   self.last, self.current_minute))
                # print('{} {} {} {}'.format('USDT', self.usdt, self.ticker, self.tq))
                self.tq += self.tq_per_order
                self.usdt -= float(self.tq_per_order * purchase_price * 1.0008)
                self.last = float(purchase_price)
                self.buy_trans[self.current_minute] = float(purchase_price)
                self.index_buy_trans[self.series.index[self.current_minute]] = purchase_price
                self.recent_buys[self.current_minute] = float(purchase_price)
                if self.consecutive_type == 'buy':
                    self.consecutive_trans[self.current_index] = purchase_price
                else:
                    if len(self.consecutive_trans) > 0:
                        self.past_consecutive.append({'type': self.consecutive_type, 'trans': self.consecutive_trans})
                    self.consecutive_type = 'buy'
                    self.consecutive_trans = {self.current_index: purchase_price}
                self.buy_list.pop(-1)
            
    def try_execute_sale(self):
        sale_price = 0
        if len(self.sell_list) > 0 and self.fill_bot==True:
            sale_price = float(self.sell_list[0])
        if len(self.sell_list) > 0 and self.fill_bot==False:
            self.index_from_top = round(self.tq/self.tq_per_order)
            if self.index_from_top-1 <= len(self.sell_list):
                sale_price = float(self.sell_list[-self.index_from_top+1])
            else:
                sale_price = float(self.sell_list[0])
        if float(self.tq) > float(self.tq_per_order) and float(self.current_price) > sale_price and sale_price not in self.recent_sales.values() and len(self.sell_list) > 0 and sale_price != 0:
            if sale_price >= self.last * 1.01 or sale_price <= self.last * 0.99:
                # print('Executing sale at: {}, current price is greater at: {}, last: {}'.format(sale_price, self.current_price,
                                                                                            #   self.last))
                # print('{} {} {} {}'.format('USDT', self.usdt, self.ticker, self.tq))
                self.tq -= self.tq_per_order
                self.usdt += (self.tq_per_order * sale_price * 0.9992)
                self.last = float(sale_price)
                self.sell_trans[self.current_minute] = float(sale_price)
                self.index_sell_trans[self.series.index[self.current_minute]] = sale_price
                self.recent_sales[self.current_minute] = float(sale_price)
                if self.consecutive_type == 'sell':
                    self.consecutive_trans[self.current_index] = sale_price
                else:
                    if len(self.consecutive_trans) > 0:
                        self.past_consecutive.append({'type': self.consecutive_type, 'trans': self.consecutive_trans})
                    self.consecutive_type = 'sell'
                    self.consecutive_trans = {self.current_index: sale_price}
                self.sell_list.pop(0)
            
    def increment(self):
        if self.current_minute < len(self.series):
            self.try_execute_purchase()
            self.try_execute_sale()
            if self.current_price > max(self.order_list) or self.current_price < min(self.order_list):
                self.update_order_list()
            if int(self.current_minute) % self.update_frequency == 0 and (self.tq != 0 and self.usdt != 0):
                self.update_lists()
                self.recent_buys = {}
                self.recent_sales = {}
            self.selling_grid.execute_current_minute()
            if self.selling_grid.usdt > 0:
                self.usdt += self.selling_grid.usdt
                self.update_lists()
                self.selling_grid.usdt = 0
            self.filter_buy_list()
            self.get_current_value()
            self.current_minute = self.selling_grid.current_minute
            if self.current_minute < len(self.series):
                self.current_index = self.series.index[self.current_minute]
                self.current_price = self.series.iloc[self.current_minute]
            else:
                print('Trading grid finished incrementing.')
        else:
            print('Trading grid finished at minute: {} out of {}.'.format(self.current_minute, len(self.series)))
            
    def execute_smart_grid(self):
        while self.current_minute < len(self.series):
            self.increment()