import os
from flask import Flask, request, make_response
import pandas as pd
from sqlalchemy import *
from flask.helpers import send_from_directory
from flask_cors import CORS
from datetime import datetime
import json
from .execute_grid import execute_grid
 
app = Flask(__name__, static_folder='../build')

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

url = "mysql://admin:vertical@database-2.cood7ompdfrc.us-east-2.rds.amazonaws.com:3306/kucoin"

engine = create_engine(url)

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
        df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        last_timestamp = df['index'].max()
        current_timestamp = datetime.now().timestamp()

        data_age = (current_timestamp - last_timestamp) / 60
        return str(data_age)

@app.route("/api/tickers")
def all_tickers():
        df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        length = len(df)
        frame = df.copy()
        frame = frame.dropna(axis=1, how='any')
        all_tickers = frame.drop('index', axis=1).columns.to_list()
        res = {"data": all_tickers, "length": length}
        return res
 
@app.route("/api/ma/<ticker>/<period>/<quantity>")
def ma(ticker, period, quantity):
        df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        ticker = str(ticker).upper()
        period = int(period)
        quantity = int(quantity)
        frame = df.copy()
        frame['index'] = pd.to_datetime(frame['index'], unit='s')
        ndf = frame.set_index('index')
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
        df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
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
        df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        data = request.json
        minutes_df = df.iloc[-int(minutes)::int(minutes)-1]
        ticker_list = []
        percent_list = []
        for obj in data['data']:
                ticker_list.append(obj['name'])
                percent_list.append(obj['percent'])
        res_df = minutes_df[ticker_list]
        res_df = res_df.copy()
        res_df.loc[2]= res_df.pct_change().iloc[-1]
        res_df['Index'] = ["Start Price", "Finish Price", "Percent Change"]
        res_df = res_df.set_index('Index')
        res_df.loc["Portfolio Percent"] = percent_list
        start_val_list = []
        quantity_list = []
        finish_val_list = []
        for count, ticker in enumerate(ticker_list):
                start_price = res_df[ticker]["Start Price"]
                percent = res_df[ticker]['Portfolio Percent']
                finish_price = res_df[ticker]["Finish Price"]
                quantity = (int(investment) * (int(percent)/100)) / float(start_price)
                quantity_list.append(quantity)
                start_val_list.append(int(investment) * (int(percent)/100))
                finish_val_list.append(quantity * finish_price)
        res_df.loc['Quantity of Coins'] = quantity_list
        res_df.loc['Start Value (USD)'] = start_val_list
        res_df.loc['Finish Value (USD)'] = finish_val_list

        res_df.loc['Difference'] = res_df.loc['Finish Value (USD)'] - res_df.loc['Start Value (USD)']
                
        res_df = res_df.swapaxes('index', 'columns')
        res_df = res_df.astype('float')
        averages = res_df.mean()
        totals = res_df.sum()
        res_df.loc['Average'] = averages
        res_df.loc['Total'] = totals
        res_df = res_df.round(2)

        total = res_df.loc['Total']['Finish Value (USD)']
        dict_df = res_df.to_dict()
        html_table = res_df.to_html()

        return {'html': html_table, 'dict': dict_df, 'total': total}, 201


# This borrow table does not return the results.

@app.route('/api/borrow/<minutes>/<investment>', methods = ['POST'])
def borrow_coins(minutes, investment):
        df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        data = request.json
        minutes_df = df.iloc[[-int(minutes)]]
        ticker_list = []
        percent_list = []
        for obj in data['data']:
                ticker_list.append(obj['name'])
                percent_list.append(obj['percent'])
        res_df = minutes_df[ticker_list]
        res_df = res_df.copy()
        res_df.rename(index={len(df)-int(minutes) :'Start Price'},inplace=True)
        res_df.loc["Portfolio Percent"] = percent_list

        start_val_list = []
        quantity_list = []
        for ticker in ticker_list:
                start_price = res_df[ticker]["Start Price"]
                percent = res_df[ticker]['Portfolio Percent']
                quantity = (int(investment) * (int(percent)/100)) / float(start_price)
                quantity_list.append(quantity)
                start_val_list.append(int(investment) * (int(percent)/100))

        res_df.loc['Liabilities (# of coins)'] = quantity_list
        res_df.loc['Start Value (USD)'] = start_val_list

        res_df = res_df.swapaxes('index', 'columns')
        res_df = res_df.astype('float')
        averages = res_df.mean()
        totals = res_df.sum()
        res_df.loc['Average'] = averages
        res_df.loc['Total'] = totals

        html_table = res_df.to_html()
        dict_df = res_df.to_dict()

        return {"html":html_table, "dict": dict_df}, 201


@app.route('/api/static/<base>/<minutes>/<investment>', methods = ['POST'])
def trade_coins(base, minutes, investment):
        df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
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
def ma_grid(base, minutes, investment):
        df = pd.read_sql("SELECT * FROM usdt_last", con=engine).astype('float')
        minutes = int(minutes)
        investment = int(investment)
        data = request.json
        trade_data = data['data']
        if base != 'USDT':
                base_change = df[base][-minutes::minutes-1].pct_change().iloc[-1]
        else:
                base_change = str(0.0)

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
                ticker_quantity, ticker2_quantity, result, buy_trans, sell_trans = execute_grid(df, minutes, name, base, spread, orders, investment*percent, period, std)

                result_dict[name] = {'results': result, 'spread': spread, 'orders': orders, 'base_currency': ticker2_quantity, 'trade_currency': ticker_quantity,
                 'buy_transactions': len(buy_trans), 'sell_transactions': len(sell_trans), 'base_ticker': base, 'trade_ticker': name, 'pair': pair}
                
                df_data[pair] = [result, spread, orders, len(buy_trans), len(sell_trans), std]

        frame = pd.DataFrame(df_data, index=['Value', 'Spread', 'Orders', 'Buy Transactions', 'Sell Transactions', 'Deviations'])
        frame = frame.swapaxes('index', 'columns')
        html_table = frame.to_html()
        result_dict['html'] = html_table
        result_dict['base_change'] = str(base_change)

        return result_dict



                        
        
        