from .getMetrics import *
import pandas as pd

def get_hodl_results(df, minutes, investment, data):
    minutes = int(minutes)
    investment = int(investment)
    start = minutes + 500
    finish = minutes
    ticker_list = [x['name'] for x in data['data']]
    percent_list = [int(x['percent']) for x in data['data']]

    start_snapshot = get_minute_snapshot(df, minutes, ticker_list)
    finish_snapshot = get_minute_snapshot(df, 0, ticker_list)
    # start_vol = get_minute_snapshot(vdf, minutes, ticker_list)
    # finish_vol = get_minute_snapshot(vdf, 0, ticker_list)
    start_value = [(x/100) * investment for x in percent_list]

    # vol_pct = ((start_vol - finish_vol)/start_vol)*100
    # rounded_vol_pct = [round(x, 2) for x in vol_pct]
    price_change = [round(float(finish_snapshot[x]) - float(start_snapshot[x]), 8) for x in range(len(start_snapshot))]
    price_change_pct = [round((float(price_change[x])/float(start_snapshot[x]))*100, 2) for x in range(len(start_snapshot))]

    grid_std, grid_std_rank = get_normalized_std(df, start=minutes, finish=0, ticker_list=ticker_list)
    liabilities = [round(float(start_value[i])/float(start_snapshot[i]), 4) for i in range(len(start_snapshot))]
    liabilities = [round_number(x) for x in liabilities]

    hodl_d = {}
    index_array = ticker_list
    hodl_d['Start Price'] = start_snapshot
    hodl_d['Finish Price'] = finish_snapshot
    # hodl_d['Price Change'] = price_change
    hodl_d['Price Change %'] = price_change_pct
    hodl_d['STD %'] = grid_std*100
    # hodl_d['Volume Change'] = rounded_vol_pct
    hodl_d['Portfolio %'] = percent_list
    hodl_d['Start Value (USD)'] = [(x/100) * investment for x in percent_list]
    hodl_d['Finish Value (USD)'] = [round(finish_snapshot[x] * liabilities[x]) for x in range(len(liabilities))]

    hodl_df = pd.DataFrame(hodl_d, index=index_array)

    hodl_average = hodl_df.mean()
    hodl_total = hodl_df.sum()
    hodl_average = [round_number(x) for x in hodl_average]
    hodl_total = [round_number(x) for x in hodl_total]
    hodl_df.loc['Average'] = hodl_average
    hodl_df.loc['Total'] = hodl_total

    html = hodl_df.to_html()
    dictionary = hodl_df.to_dict()
    total = hodl_df['Finish Value (USD)']['Total']

    result = {'html': html, 'dict': dictionary, 'total': total}
    return result