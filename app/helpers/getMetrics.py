from ..cleanDF import cleanDF

def get_normalized_std(frame, start, finish, ticker_list):
    if start > len(frame):
        print_message = {'frame length': len(frame), 'minutes': start, 'finish': finish, 'ticker_list': ticker_list,
        'minutes type': type(start), 'finish_type': type(finish)}
        print(print_message)
        error_list = ['Insufficient Data' for x in ticker_list]
        return error_list, error_list
    
    if finish == 0:
        previous_day = cleanDF(frame[-start:]).drop('index', axis=1).astype('float')
    else:
        previous_day = cleanDF(frame[-start:-finish]).drop('index', axis=1).astype('float')

    previous_day_std = (previous_day.std()/previous_day.mean())
    limited_prev_std = round_series(previous_day_std[ticker_list])
    previous_day_std_rank = previous_day_std.rank()[ticker_list]
    return limited_prev_std, previous_day_std_rank

def get_average(frame, start, finish, ticker_list):
    if start > len(frame):
        print_message = {'frame length': len(frame), 'minutes': start, 'finish': finish, 'ticker_list': ticker_list,
        'minutes type': type(start), 'finish_type': type(finish)}
        print(print_message)
        error_list = ['Insufficient Data' for x in ticker_list]
        return error_list
    
    if finish == 0:
        frame = frame.iloc[-start:].astype('float')
    else:
        frame = frame.iloc[-start:-finish].astype('float')
    all_averages = frame.mean()
    ticker_averages = round_series(all_averages[ticker_list])
    return ticker_averages
    
def get_minute_snapshot(frame, minutes, ticker_list):
    if minutes > len(frame):
        print_message = {'frame length': len(frame), 'minutes': minutes, 'ticker_list': ticker_list,
        'minutes type': type(minutes)}
        print(print_message)
        return ["Insufficient Data" for x in ticker_list]

    if minutes != 0:
        minute_frame = frame.iloc[-minutes:].astype('float')
        snapshot = minute_frame.iloc[-minutes].dropna()[ticker_list]
    else:
        snapshot = frame.iloc[-1].astype('float').dropna()[ticker_list]

    rounded_snapshot = round_series(snapshot)
    return rounded_snapshot

def get_net_change(frame, start, finish, ticker_list):
    if finish == 0:
        frame = frame.iloc[-start:].astype('float')
    else:
        frame = frame.iloc[-start:-finish].astype('float')

    pct_frame = frame.pct_change()
    net = round_series(pct_frame[ticker_list].sum())
    return net

def round_number(num):
    num=f"{float(num):.9f}"
    if '.' in num:
        decimal_index = num.index('.')
        round_decimals = 7 - decimal_index
        if round_decimals < 0:
            round_decimals = 0
        while num[-1] == 0:
            num = num[:-1]
        num = round(float(num), round_decimals)
    else:
        print("No '.' value in string number.")
    return num

def round_series(series):
    series = series.astype('str')
    for dex, val in series.items():
        val = f"{float(val):.9f}"
        decimal_index = val.index('.')
        round_decimals = 5 - int(decimal_index)
        if round_decimals < 0:
            round_decimals = 0
        if val[decimal_index-1] == '0':
            round_decimals += 1
            i = 1
            if decimal_index + i < len(val)-1:
                while val[decimal_index+i] == '0':
                    round_decimals += 1
                    i += 1
                    try:
                        val[decimal_index+i]
                    except:
                        print(val)
                        break
        series[dex] = round(float(val), round_decimals)
    return series