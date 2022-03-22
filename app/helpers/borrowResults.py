from .getMetrics import *
import pandas as pd

def get_borrow_data(df, minutes, investment, data):
    minutes = int(minutes)
    investment = int(investment)
    start = minutes + 500
    finish = minutes
    ticker_list = [x['name'] for x in data['data']]
    percent_list = [int(x['percent']) for x in data['data']]

    start_snapshot = get_minute_snapshot(df, minutes, ticker_list)
    # start_vol = get_minute_snapshot(vdf, minutes, ticker_list)
    # relative_value_snapshot = get_minute_snapshot(rv_df, minutes, ticker_list) * 100
    # range_snapshot = get_minute_snapshot(range_df, minutes, ticker_list) * 100

    start_value = [(x/100) * investment for x in percent_list]
    liabilities = [round(float(start_value[i])/float(start_snapshot[i]), 4) for i in range(len(start_snapshot))]
    liabilities = [round_number(x) for x in liabilities]

    # average_vol = get_average(vdf, start=start, finish=finish, ticker_list=ticker_list)
    # average_price = get_average(df, start, finish, ticker_list)
    previous_day_std, previous_day_std_rank = get_normalized_std(df, start=start, finish=finish, ticker_list=ticker_list)
    # prev_day_vol_std, prev_day_vol_std_rank = get_normalized_std(vdf, start=start, finish=finish, ticker_list=ticker_list)
    net_pc = get_net_change(df, start, finish, ticker_list) * 100
    previous_day_std = previous_day_std*100
    # prev_day_vol_std = prev_day_vol_std*100

    result_d = {}
    index_array = ticker_list
    result_d['Start Price'] = start_snapshot
    # result_d['Start Volume'] = start_vol
    result_d['Portfolio %'] = percent_list
    result_d['Start Value (USD)'] = start_value
    result_d['Liabilities (# of coins)'] = liabilities
    result_d['24h Price STD %'] = previous_day_std
    # result_d['24h Vol STD %'] = prev_day_vol_std
    # result_d['24h Relative Value %'] = relative_value_snapshot
    # result_d['24h Range %'] = range_snapshot/2
    result_d['24h Net Price Change %'] = net_pc

    borrow_df = pd.DataFrame(result_d, index=index_array)
    average = borrow_df.mean()
    total = borrow_df.sum()
    average = [round_number(x) for x in average]
    total = [round_number(x) for x in total]
    borrow_df.loc['Average'] = average
    borrow_df.loc['Total'] = total

    html = borrow_df.to_html()
    dictionary = borrow_df.to_dict()
    result = {'html': html, 'dict': dictionary}

    return result
