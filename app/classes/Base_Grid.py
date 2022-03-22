class Base_Grid:
    def __init__(self, df, investment, minutes, orders, spread, period, ticker, grid_type):
        self.df = df
        if len(df) > minutes:
            self.limited_df = df.iloc[len(df)-minutes:]
        else:
            self.limited_df = df
            
        self.df = df
        self.investment = int(investment)
        self.minutes = int(minutes)
        self.orders = int(orders)
        self.spread = int(spread)
        self.period = int(period)
        self.ticker = str(ticker)
        self.series = self.limited_df.loc[:, self.ticker].astype('float')
        self.entire_series = self.df.loc[:, self.ticker]
        self.start_price = float(self.series.iloc[0])
        self.grid_type = grid_type
        
        self.order_list = [self.round_number(((1-self.spread/200)+x*self.spread/self.orders/100) * self.start_price) 
                           for x in range(self.orders+1)]
        self.stringed_order_list = [f"{float(x):.9f}" for x in self.order_list]
        
        self.start_tq = investment / self.start_price
        self.tq = float(self.investment/self.start_price)
        self.tq_per_order = float(self.tq/self.orders)
        
        self.sell_list = []
        self.stringed_order_list = [f"{float(x):.9f}" for x in self.order_list]
        self.last = 0
        self.ma = self.entire_series.rolling(self.period).mean().dropna()
        if self.minutes < len(self.entire_series):
            self.ma = self.ma.iloc[-minutes:]
        self.finish_price = self.series.iloc[-1]
        self.index_sell_trans = {}
        self.index_buy_trans = {}
        
        self.current_assets = []
        self.current_value = []
        self.sell_trans = {}
        self.buy_trans = {}
        self.recent_buys = {}
        self.recent_sales = {}
        self.usdt = 0
        self.current_minute = 0
        self.current_index = self.series.index[self.current_minute]
        self.index_from_top = 0
        self.current_price = float(self.series.iloc[self.current_minute])
        self.consecutive_type = None
        self.consecutive_trans = {}
        self.past_consecutive = []
        self.debt_list = []
        exec("self.{} = self.tq".format(self.ticker))
        
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
        print('orders are: {}'.format(orders))