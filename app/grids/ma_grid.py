import pandas as pd

def get_ma_list(df, minutes, ticker1, ticker2, period, deviations):
    if period != 0:
        if len(df) - period < minutes:
            # print('Error, not enough data to calculate MA + test for all minutes.')
            raise Exception('Database length is insufficient to handle minutes+period.')
        
        elif ticker2 == 'USDT':
            rolling_df = df[[ticker1]].dropna().rolling(period).mean().dropna()[-minutes:]
            std = df[[ticker1]].rolling(period).std().dropna().iloc[-minutes:]
            low_roller = rolling_df - (deviations*std)
            high_roller = rolling_df + (deviations*std)
        else:
            prices = df[ticker1]/df[ticker2]
            frame = pd.DataFrame(prices)
            rolling_df = frame.dropna().rolling(period).mean().dropna()[-minutes:]
            std = frame.dropna().rolling(period).std().dropna().iloc[-minutes:]
            low_roller = rolling_df - (deviations*std)
            high_roller = rolling_df + (deviations*std)
        
        low_roller = low_roller.astype('float')
        high_roller = high_roller.astype('float')
        
        low_list = low_roller.squeeze().tolist()
        high_list = high_roller.squeeze().tolist()
                
        return low_list, high_list

def get_order_list(orders, spread, start_price):
    factor = spread/(orders-1)/100
    order_list = [start_price * (1-(spread/200)+x*factor) for x in range(orders)]
    return order_list

def get_per_order_quantity(orders, investment, start_price):
    start_value = investment/2/start_price
    per_order_quantity = start_value/orders*1.5
    return per_order_quantity

def filter_order_list(order_list, high_list, low_list, price_list, minute):
    sell_list = [x for x in order_list if x > high_list[minute] and x > price_list[minute]]
    buy_list = [x for x in order_list if x < low_list[minute] and x < price_list[minute]]
    sell_list.sort()
    buy_list.sort()
    return sell_list, buy_list

def adjust_quantities(t1q, t2q, phq, last, last_type, base, base_list, minute):
    if base == 'USDT':
        if last_type == 'purchase':
            t1q += (phq * .9992)
            t2q -= (phq * last)
        elif last_type == 'sale':
            t1q -= (phq)
            t2q += (phq * last * .9992)
    elif base != 'USDT':
        if last_type == 'purchase':
            t1q += (phq * .9992)
            t2q -= (phq * last)
        if last_type == 'sale':
            t1q -= (phq)
            t2q += (phq * last * .9992)
    return t1q, t2q

def initial_purchases(investment, ticker_price_list, base_list):
    half_inv = investment/2
    t1q = half_inv/ticker_price_list[0]
    t2q = half_inv/base_list[0]
    # print("Buying initial coins... Buying {} of {} for {} USD. Buying {} of {} for {} USD.".format(t1q, ticker, investment/2, t2q, base, investment/2))
    return t1q, t2q

def get_profit(t1q, price_list, t2q, base_list):
    t1v = t1q * price_list[-1]
    t2v = t2q * base_list[-1]
    result = t1v + t2v
    # print("Final quantities: {} of {}, {} of {}.\n Final value is: {}".format(t1q, ticker, t2q, base, result))
    return result

def get_price_lists(df, ticker, base, minutes):
    one = df[ticker]
    base = base
    if base == 'USDT':
        base_list = [1 for x in range(minutes)]
        price_list = one.iloc[-minutes:].to_list()
    else:
        base_list = df[base].iloc[-minutes:].to_list()
        a = one.iloc[-minutes:]/df[base][-minutes:]
        price_list = a.to_list()
    
    ticker_price_list = df[ticker].iloc[-minutes:].to_list()
    
    return ticker_price_list, price_list, base_list

def get_graph_lines(df, base, ticker, minutes, buy_trans, sell_trans, order_list):
    ticker_df = df[ticker]
    if base == 'USDT':
        base_df = df['USDC']
    else:
        base_df = df[base]
        
    price_df = (ticker_df/base_df).iloc[-minutes:]
    start = price_df.index[0]
    over_start = price_df/price_df.iloc[0]
    index = over_start.index
    
    sell_mins = [x['minute'] for x in sell_trans]
    buy_mins = [x['minute'] for x in buy_trans]
    
    buy_prices = [over_start.iloc[x] for x in buy_mins]
    sale_prices = [over_start.iloc[x] for x in sell_mins]
    
    sale_x = [index[x]-start for x in sell_mins]
    buy_x = [index[x]-start for x in buy_mins]
    over_start.index = over_start.index-start
    
    order_list = (order_list/price_df.iloc[0])
    
    return {'ticker': ticker, 'price_line': over_start, 'buy_line':[buy_x, buy_prices], 'sell_line': [sale_x, sale_prices]}

def ma_grid(df, investment, ticker, base, minutes, spread, orders, period, std):
    pd.set_option("display.precision", 9)
    
    ticker_price_list, price_list, base_list = get_price_lists(df, ticker, base, minutes)
    low_list, high_list = get_ma_list(df, minutes, ticker, base, period, std)
    start_price = df[ticker].iloc[-minutes]
    order_list = get_order_list(orders, spread, price_list[0])
    sell_list, buy_list = filter_order_list(order_list, high_list, low_list, price_list, 0)
    phq = get_per_order_quantity(orders, investment, start_price)
    buy_trans, sell_trans = [], []
    t1q, t2q = initial_purchases(investment, ticker_price_list, base_list)
    last = 0
    last_type = ''
    for num in range(len(price_list)):
        trans = False
        price = price_list[num]
        high_price = high_list[num]
        low_price = low_list[num]
        if price >= high_price:
            if len(sell_list) > 0:
                #print('price: {}, sell_list[0]: {}, sell_list[-1]: {}, last: {}, t1q: {}, phq: {}.'.format(price, sell_list[0], sell_list[-1], last, t1q, phq))
                while price >= sell_list[0] and sell_list[0] != last and t1q > phq:
                    # print("Price: {} is greater than high price: {} and sell_list[0]: {}. Executing sale!".format(price, high_price, sell_list[0]))
                    last = sell_list.pop(0)
                    last_type = 'sale'
                    t1q, t2q = adjust_quantities(t1q, t2q, phq, last, last_type, base, base_list, num)
                    sell_trans.append({'price': last, 'minute': num})
                    sell_list, buy_list = filter_order_list(order_list, high_list, low_list, price_list, num)
                    trans = True
                    if len(sell_list) == 0:
                        break

        if price <= low_price:
            if len(buy_list) > 0:
                while price <= buy_list[-1] and buy_list[-1] != last and t2q > phq * buy_list[-1]:
                    # print("Price: {} is less than low_price: {} and buy_list[-1]: {}. Executing purchase!".format(price, low_price, buy_list[-1]))
                    last = buy_list.pop(-1)
                    last_type = 'purchase'
                    buy_trans.append({'price': last, 'minute': num, 'high': high_price, 'low': low_price})
                    t1q, t2q = adjust_quantities(t1q, t2q, phq, last, last_type, base, base_list, num)
                    sell_list, buy_list = filter_order_list(order_list, high_list, low_list, price_list, num)
                    trans = True
                    if len(buy_list) == 0:
                        break

        if t1q < 0 or t2q < 0:
            print('Quantity Error! t1q: {} t2q: {}.'.format(t1q, t2q))
        # if trans == True:
        #     print(num)
        #     print("{} quantity: {}. {} quantity: {}".format(ticker, t1q, base, t2q))
        if num == len(price_list)-1:
            result = get_profit(t1q, ticker_price_list, t2q, base_list)

        if len(buy_list) == 0:
            # print('Buy list length is 0 at minute: {}. MOVING ORDER LIST!'.format(num))
            order_list = get_order_list(orders, spread, price_list[num])
            sell_list, buy_list = filter_order_list(order_list, high_list, low_list, price_list, num)
        if len(sell_list) == 0:
            # print('Sell list length is 0 at minute: {}. MOVING ORDER LIST!'.format(num))
            order_list = get_order_list(orders, spread, price_list[num])
            sell_list, buy_list = filter_order_list(order_list, high_list, low_list, price_list, num)

        if price < min(order_list) or price > max(order_list):
            # print("Price: {} is outside of order list price range: {} to {}. MOVING ORDER LIST!".format(price, min(order_list), max(order_list)))
            order_list = get_order_list(orders, spread, price_list[num])
            sell_list, buy_list = filter_order_list(order_list, high_list, low_list, price_list, num)
        else:
            sell_list, buy_list = filter_order_list(order_list, high_list, low_list, price_list, num)
    #     print("Sell List: {} Buy List: {}\n".format(len(sell_list), len(buy_list)))
    
    graph_lines = get_graph_lines(df, base, ticker, minutes, buy_trans, sell_trans, order_list)
    
    return result, buy_trans, sell_trans, t1q, t2q, graph_lines