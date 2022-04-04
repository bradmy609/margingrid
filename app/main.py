import os
from flask import Flask, request
import pandas as pd
from sqlalchemy import *
from flask.helpers import send_from_directory
from flask_cors import CORS
from datetime import datetime
from .execute_grid import execute_grid
from .cleanDF import cleanDF
from .grids.ma_grid import ma_grid
from .helpers.borrowResults import get_borrow_data
from .helpers.hodlResults import get_hodl_results
from .classes.Selling_Grid import Selling_Grid
from .classes.Smart_Grid import Smart_Grid
from .classes.Grapher import Grid_Grapher

 
app = Flask(__name__, static_folder='../build')

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

url = "mysql://admin:vertical@database-2.cood7ompdfrc.us-east-2.rds.amazonaws.com:3306/kucoin"

engine = create_engine(url)

# vdf = cleanDF(pd.read_sql('SELECT * FROM usdt_vol LIMIT 0, 1000', con=engine).astype('float'))
# top_30_vol = vdf.drop('index', axis=1).mean().sort_values().tail(30)
# top_30_vol_tickers = top_30_vol.index.to_list()
# top_30_vol_tickers.insert(0, '`index`')
# top_30_vol_tickers_string = ', '.join(top_30_vol_tickers)
# og_df = cleanDF(pd.read_sql('SELECT {} FROM usdt_last LIMIT 0, 35000'.format(top_30_vol_tickers_string), con=engine).astype('float'))

temp = pd.read_sql('Select * FROM PolygonVW Limit 0, 1', con=engine)
temp_columns = ','.join(temp.drop('index', axis=1).columns.to_list())
og_df = cleanDF(pd.read_sql("SELECT {} FROM PolygonVW LIMIT 300000, 249780".format(temp_columns), con=engine).rename({'ts': 'index'}, axis=1).astype('float32'))

# og_df = cleanDF(pd.read_sql("SELECT * FROM usdt_last LIMIT 0, 15000", con=engine).astype('float'))
# vdf = cleanDF(pd.read_sql("SELECT * FROM usdt_vol LIMIT 0, 11000", con=engine).astype('float'))
# rv_df = cleanDF(pd.read_sql("SELECT * FROM relative_value LIMIT 0, 1000", con=engine).astype('float'))
# range_df = cleanDF(pd.read_sql("SELECT * FROM 24h_range LIMIT 0, 1000", con=engine).astype('float'))

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route("/api/age")
def data_age():
        # df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        df = og_df.loc[:]
        if 'ts' in df.columns:
                last_timestamp = df['ts'].max()
        else:
                last_timestamp = df['index'].max()
        current_timestamp = datetime.now().timestamp()

        data_age = (current_timestamp - last_timestamp) / 60
        return str(data_age)

@app.route("/api/tickers")
def all_tickers():
        # df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        df = og_df.loc[:]
        length = len(df)
        frame = df
        frame = frame[frame.iloc[0].dropna().index]
        frame.fillna(value=0, inplace=True)
        all_tickers = frame.drop('index', axis=1).columns.to_list()
        res = {"data": all_tickers, "length": length}
        return res
 
@app.route("/api/ma/<ticker>/<period>/<quantity>")
def ma(ticker, period, quantity):
        # df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        df = og_df.copy()
        ticker = str(ticker).upper()
        period = int(period)
        quantity = int(quantity)
        df = df[df.iloc[0].dropna().index]
        df['index'] = pd.to_datetime(df['index'], unit='s')
        ndf = df.set_index('index')
        ticker_df = ndf[[ticker]]
        rolling_ticker_df = ticker_df.rolling(period).mean().iloc[::period].rolling(quantity).mean().dropna(how='all')

        if len(rolling_ticker_df) < quantity:
                ma = rolling_ticker_df
        else:
                ma = rolling_ticker_df.iloc[-(quantity):]
        
        ma.index = ma.index.astype('str')
        ma_dict = ma.to_dict()
        return ma_dict

@app.route("/api/pricedelta/<startMinutes>/<stopMinutes>/<top>/<quantity>")
def reroute(startMinutes, top, quantity, stopMinutes=0):
        # df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        df = og_df.copy()
        df = df[df.iloc[0].dropna().index]

        startMinutes = int(startMinutes)
        if startMinutes > len(df):
                startMinutes = len(df)
        stopMinutes = int(stopMinutes)
        quantity = int(quantity)

        minDelta = startMinutes - stopMinutes;
        
        if top == "true" or top == "True":
                top = True
                order = "(Greatest to Least)"
        if top == "false" or top == "False":
                top = False
                order = "(Least to Greatest)"

        if stopMinutes != 0:
                res = df[-startMinutes:-stopMinutes]
        elif stopMinutes == 0 and startMinutes == 0:
                res = df
                minDelta = len(df)
        else:
                res = df[-startMinutes:]

        deltap = res.pct_change().sum().drop('index')
        deltap_sorted = pd.DataFrame(deltap.sort_values(ascending=top).tail(quantity), columns=['Price Change (%)'])
        deltap_sorted['Window Minutes'] = [minDelta for x in range(len(deltap_sorted))]
        deltap_sorted = deltap_sorted[::-1]
        deltap_sorted['Rank' + order] = [x+1 for x in range(len(deltap_sorted))]
        deltap_table = deltap_sorted.to_html()
        return deltap_table

# The below route function returns a borrow table that includes the results, such as profit and finish price. 

@app.route('/api/hodl/<minutes>/<investment>', methods = ['POST'])
def hodl_table(minutes, investment):
        # df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        df = og_df.copy()
        data = request.json
        minutes = int(minutes)
        investment = int(investment)

        if minutes > len(df):
                minutes = len(df)-1

        results = get_hodl_results(df, minutes, investment, data)

        return results, 201


# This borrow table does not return the results.

@app.route('/api/borrow/<minutes>/<investment>', methods = ['POST'])
def borrow_coins(minutes, investment):
        # df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        df = og_df.copy()
        data = request.json
        minutes = int(minutes)
        investment = int(investment)

        print({'minutes': minutes, 'investment': investment, 'data': data})

        if minutes > len(df):
                minutes = len(df)-1
                
        result = get_borrow_data(df, minutes, investment, data)

        return result, 201


@app.route('/api/static/<base>/<minutes>/<investment>', methods = ['POST'])
def trade_coins(base, minutes, investment):
        # df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        df = og_df.copy()
        minutes = int(minutes)
        investment = int(investment)
        base = str(base)

        data = request.json
        trade_data = data['data']
        if base != 'USDT':
                base_change = df[base][-minutes::minutes-1].pct_change().iloc[-1]
        else:
                base_change = '0'

        result_dict = {}
        df_data = {}
        for d in trade_data:
                spread = int(d['spread'])
                orders = int(d['orders'])
                name = str(d['name'])
                percent = float(d['percent'])/100
                pair = '{}/{}'.format(name, base)
                ticker_quantity, ticker2_quantity, result, buy_trans, sell_trans = execute_grid(df, minutes, name, base, spread, orders, investment*percent)

                result_dict[name] = {'static_grid': result, 'spread': spread, 'orders': orders, 'base_currency': ticker2_quantity, 'trade_currency': ticker_quantity,
                 'buy_transactions': len(buy_trans), 'sell_transactions': len(sell_trans), 'base_ticker': base, 'trade_ticker': name, 'pair': pair}
                
                df_data[pair] = [result, spread, orders, len(buy_trans), len(sell_trans)]

        frame = pd.DataFrame(df_data, index=['Value', 'Spread', 'Orders', 'Buy Transactions', 'Sell Transactions'])
        frame = frame.swapaxes('index', 'columns')
        html_table = frame.to_html()
        result_dict['html'] = html_table
        result_dict['base_change'] = str(base_change)

        return result_dict

@app.route('/api/grid/ma/<base>/<minutes>/<investment>', methods = ['POST'])
def ma_dynamic_grid(base, minutes, investment):
        # df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        df = og_df.copy()
        minutes = int(minutes)
        investment = int(investment)

        data = request.json
        trade_data = data['data']

        if base != 'USDT':
                base_change = df[base][-minutes::minutes-1].pct_change().iloc[-1]
        else:
                base_change = '0.0'

        result_dict = {}
        df_data = {}
        for d in trade_data:
                spread = int(d['spread'])
                orders = int(d['orders'])
                name = str(d['name'])
                percent = float(d['percent'])/100
                period = int(d['period'])
                std = int(d['std'])
                if minutes + period >= len(df):
                        period = len(df) - minutes
                pair = '{}/{}'.format(name, base)

                result, buy_trans, sell_trans, t1q, t2q = ma_grid(df, investment*percent, name, base, minutes, spread, orders, period, std)

                result_dict[name] = {'results': result, 'spread': spread, 'orders': orders, 'base_currency': t2q, 'trade_currency': t1q,
                 'buy_transactions': len(buy_trans), 'sell_transactions': len(sell_trans), 'base_ticker': base, 'trade_ticker': name, 'pair': pair}
                
                df_data[pair] = [result, spread, orders, len(buy_trans), len(sell_trans), std]

        frame = pd.DataFrame(df_data, index=['Value', 'Spread', 'Orders', 'Buy Transactions', 'Sell Transactions', 'Deviations'])
        frame = frame.swapaxes('index', 'columns')
        html_table = frame.to_html()
        result_dict['html'] = html_table
        result_dict['base_change'] = str(base_change)

        return result_dict

@app.route('/api/grid/smart/<minutes>/<investment>', methods=['POST'])
def smart_grid_borrow(minutes, investment):
        if not minutes or not investment:
                return "Record not found", 400
        minutes = int(minutes)
        investment = int(investment)
        data = request.json['data']
        s = data['settings']
        bs = data['borrowSettings']
        ts = data['tradeSettings']
        offset = int(s['offset'])
        base = str(s['base'])
        if (minutes + offset) > len(og_df):
                offset = 0
                minutes = len(og_df)

        orders, spread, ticker, marketSell, onlySellAbove, period, gridType = bs.values()
        if offset != 0:
                selling_grid = Selling_Grid(og_df[:-offset], investment, minutes, int(orders), int(spread), str(ticker), marketSell, onlySellAbove, int(period), gridType, base=base)
        else:
                selling_grid = Selling_Grid(og_df, investment, minutes, int(orders), int(spread), str(ticker), marketSell, onlySellAbove, int(period), gridType, base=base)
        torders, tspread, tticker, updateFrequency, tperiod, tgridType, maInd, fillBot, repeatSells, repeatBuys = ts.values()
        if offset != 0:
                smart_grid = Smart_Grid(selling_grid, og_df[:-offset], str(tticker), int(torders), int(tspread), investment, minutes, int(updateFrequency), int(tperiod), str(tgridType), maInd, fillBot, repeatSells, repeatBuys)
        else:
                smart_grid = Smart_Grid(selling_grid, og_df, str(tticker), int(torders), int(tspread), investment, minutes, int(updateFrequency), int(tperiod), str(tgridType), maInd, fillBot, repeatSells, repeatBuys)
        smart_grid.execute_smart_grid()
        grapher = Grid_Grapher(smart_grid)
        results_table, profit, debt, assets = grapher.get_info()
        cv = smart_grid.current_value
        low_res_cv = cv[::100]
        sgHtml = grapher.smart_grid_html()
        selling_grid = grapher.selling_grid_html()
        series_percents = grapher.percent_profit.dropna()*100
        percent_profit = series_percents.to_list()
        low_res_percent_profit = percent_profit[::100]
        results = {'resultsTable': results_table, 'profit': profit, 'debt': debt, 'assets': assets, 'cv': low_res_cv, 'sgHtml': sgHtml, 'selling_grid': selling_grid, 'percent_profit': low_res_percent_profit}
        return results, 201
