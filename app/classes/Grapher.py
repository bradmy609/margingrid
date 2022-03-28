import matplotlib.pyplot as plt
import base64
import pandas as pd
from io import BytesIO
from matplotlib.figure import Figure

class Grid_Grapher:
    
    def __init__(self, grid):
        self.grid = grid
        self.selling_grid = grid.selling_grid
        self.percent_profit = ((pd.Series(self.grid.current_assets) - pd.Series(self.grid.selling_grid.debt_list)) / pd.Series(self.grid.selling_grid.debt_list)).fillna(0)
        
        self.slow = grid.ma
        self.fast = grid.fast_ma
        self.diff = grid.diff
        self.dstd = grid.dstd
        
        self.above = False
        self.bot_below = False
        self.above_cross_points = {}
        self.below_cross_points = {}
        self.bot_cross_above = {}
        self.bot_cross_below = {}
        
    def trade_grid_graph(self):        
        series_avg = self.grid.series.mean()
        stop_line_dex = [x for x in self.grid.stop_line.index]

        plt.plot(self.grid.series)
        plt.plot([self.grid.series.index[0] for x in range(len(self.grid.start_buy_list))], self.grid.start_buy_list, 'h', color='green')
        plt.plot([self.grid.series.index[0] for x in range(len(self.grid.start_sell_list))], self.grid.start_sell_list, 'h', color='red')
        plt.plot(self.grid.index_buy_trans.keys(), self.grid.buy_trans.values(), 'h', color='green')
        plt.plot(self.grid.index_sell_trans.keys(), self.grid.sell_trans.values(), 'h', color='red')
        plt.plot(self.grid.ma)
        plt.plot(stop_line_dex, [series_avg if str(x) != 'nan' else None for x in self.grid.stop_line])
        
    def ma_diff_graph(self):
        for count, val in self.diff.items():
            if count in self.dstd.index:
                if val > self.dstd[count] and self.above==False:
                    self.above=True
                    self.above_cross_points[count] = val
                if val < self.dstd[count] and self.above==True:
                    self.above=False
                    self.below_cross_points[count] = val
        for count, val in self.diff.items():
            if count in self.dstd.index:
                if val < -self.dstd[count] and self.bot_below==False:
                    self.bot_below=True
                    self.bot_cross_below[count] = val
                if val > -self.dstd[count] and self.bot_below==True:
                    self.bot_below=False
                    self.bot_cross_above[count] = val
                    
        plt.plot([x for x in self.diff.index], [self.dstd[x] if x in self.dstd.index else None for x in self.diff.index])
        plt.plot([x for x in self.diff.index], [-self.dstd[x] if x in self.dstd.index else None for x in self.diff.index])
        plt.plot(self.diff)
        
        plt.plot(pd.Series(self.above_cross_points), 'h')
        plt.plot(pd.Series(self.below_cross_points), 'h')
        plt.plot(pd.Series(self.bot_cross_below), 'h')
        plt.plot(pd.Series(self.bot_cross_above), 'h')

    def stop_line_graph(self):
        plt.plot(self.grid.stop_line)
        
    def selling_grid_graph(self):
        self.selling_grid.graph()
        plt.plot(self.selling_grid.ma)

    def selling_grid_html(self):
        fig=Figure()
        ax=fig.subplots()
        ax.plot(self.grid.selling_grid.series)
        ax.plot([self.grid.selling_grid.series.index[0] for x in range(len(self.grid.selling_grid.start_sell_list))], self.grid.selling_grid.start_sell_list, 'h', color='red')
        ax.plot(self.grid.selling_grid.index_sell_trans.keys(), self.grid.selling_grid.sell_trans.values(), 'h', color='red')
        buf=BytesIO()
        fig.savefig(buf, format='png')
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        html = f"<img src='data:image/png;base64,{data}'/>"
        return html
        
    def current_value_graph(self):
        plt.plot(self.grid.current_value)

    def current_value_html(self):
        fig = Figure()
        ax = fig.subplots()
        ax.plot(self.grid.current_value)
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format='png')
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        html = f"<img src='data:image/png;base64,{data}'/>"
        return html

    def smart_grid_html(self):
        fig = Figure()
        ax = fig.subplots()
        series_avg = self.grid.series.mean()
        stop_line_dex = [x for x in self.grid.stop_line.index]
        
        ax.plot(self.grid.series)
        ax.plot([self.grid.series.index[0] for x in range(len(self.grid.start_buy_list))], self.grid.start_buy_list, 'h', color='green')
        ax.plot([self.grid.series.index[0] for x in range(len(self.grid.start_sell_list))], self.grid.start_sell_list, 'h', color='red')
        ax.plot(self.grid.index_buy_trans.keys(), self.grid.buy_trans.values(), 'h', color='green')
        ax.plot(self.grid.index_sell_trans.keys(), self.grid.sell_trans.values(), 'h', color='red')
        ax.plot(self.grid.ma)
        ax.plot(stop_line_dex, [series_avg if str(x) != 'nan' else None for x in self.grid.stop_line])
        
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        html = f"<img src='data:image/png;base64,{data}'/>"
        return html
        
    def percent_profit_graph(self):
        plt.plot(self.percent_profit)
        
    def get_lowest_details(self):
        sorted_pp = self.percent_profit.sort_values()
        lowest_index = sorted_pp.index[0]
        lowest_percent = sorted_pp.iloc[0]
        liquidated = lowest_percent < -0.17
        lowest_value = min(self.grid.current_value)
        return {'lowest_percent': lowest_percent, 'lowest_index': lowest_index, 'max_margin_liquidated': liquidated,
               'lowest_price': lowest_value}
        
    def get_avg_trans_price(self):
        avg_sell = sum(self.grid.sell_trans.values())/len(self.grid.sell_trans)
        avg_buy = sum(self.grid.buy_trans.values())/len(self.grid.buy_trans)
        return {'average_sell': avg_sell, 'average_buy': avg_buy}
        
    def get_info(self):
        res_info = {}
        info = {}
        index = [self.grid.sell_ticker, self.grid.ticker, 'USDT']
        info['Start Quantity'] = [self.grid.selling_grid.start_tq, 0, 0]
        info['Start Value'] = [self.grid.selling_grid.start_tq * self.grid.selling_grid.start_price, 0, 0]
        info['Finish Quantity'] = [self.grid.selling_grid.tq, self.grid.tq, self.grid.usdt]
        info['Finish Value'] = [(self.grid.selling_grid.tq) * self.grid.selling_grid.finish_price, round(self.grid.tq*self.grid.finish_price, 2), round(self.grid.usdt, 2)]
        info['Net Value'] = [-(self.grid.selling_grid.start_tq - self.grid.selling_grid.tq) * self.grid.selling_grid.finish_price, round(self.grid.tq*self.grid.finish_price, 2), round(self.grid.usdt, 2)]
        infoFrame = pd.DataFrame(info, index)
        totals = infoFrame.sum()
        infoFrame.loc['Total'] = totals
        html = infoFrame.to_html()
        profit = infoFrame['Net Value']['Total']
        debt = infoFrame.iloc[0]['Net Value'].sum()
        assets = infoFrame.iloc[1:3]['Net Value'].sum()
        return html, profit, debt, assets#, infoFrame