from sqlalchemy import *
import pandas as pd
import math

pd.set_option("display.precision", 9)

def get_ma_list(df, minutes, ticker1, ticker2, period, deviations):
    if period != 0:
        if len(df) - period < minutes:
            # print('Error, not enough data to calculate MA + test for all minutes.')
            raise Exception('Database length is insufficient to handle minutes+period.')
        
        elif ticker2 == 'USDT':
            rolling_df = df[[ticker1]].dropna(how='all', axis=1).rolling(period).mean().dropna(how='all', axis=0)[-minutes:]
            std = df[[ticker1]].rolling(period).std().iloc[-minutes:]
            low_roller = rolling_df - (deviations*std)
            high_roller= rolling_df + (deviations*std)
        else:
            prices = df[ticker1]/df[ticker2]
            frame = pd.DataFrame(prices)
            rolling_df = frame.dropna(how='all', axis=1).rolling(period).mean().dropna(how='all', axis=0)[-minutes:]
            std = frame.rolling(period).std().iloc[-minutes:]
            low_roller = rolling_df - (deviations*std)
            high_roller = rolling_df + (deviations*std)
        
        low_roller = low_roller.astype('float')
        high_roller = high_roller.astype('float')
        
        low_list = low_roller.squeeze().tolist()
        high_list = high_roller.squeeze().tolist()
                
        return low_list, high_list

def reset_order_lists(order_list, price_list, minute=0, orders=0, buy_list=[], sell_list=[], last=0, spread=0, period=0, last_index=None):
    if type(order_list[0]) == list and orders:
        low_roller = order_list[0]
        high_roller = order_list[1]
        low_roller_start = low_roller[minute]
        high_roller_start = high_roller[minute]
        half_orders = int(orders/2)
        half_spread = spread/2
        order_factor = half_spread/half_orders/100
        low_orders = [(float(low_roller_start))*(1-(order_factor*x)) for x in range(half_orders) if x != last_index['buy']]
        high_orders = [(float(high_roller_start))*(1+(order_factor*x)) for x in range(half_orders) if x != last_index['sell']]
    
    if not sell_list and not buy_list and minute==0:
        if type(order_list[0]) != list:
            # print('Orders are 0. Unless you are instantiating initial lists, please input orders.')
            buy_list = [x for x in order_list if x < price_list[0]]
            sell_list = [x for x in order_list if x > price_list[0]]
        else:
            # print('Orders are 0. Nested lists were input. Creating buy/sell lists from nested order_list.')
            buy_list = [x for x in low_orders if x < price_list[0]]
            sell_list = [x for x in high_orders if x > price_list[0]]
        
    
    if len(buy_list) + len(sell_list) < orders-1:
        if type(order_list[0]) != list:
            for order_price in order_list:
                #print('Last price is: {} and order price is: {}'.format(last, order_price))
                if float(order_price) < float(price_list[minute]) and float(order_price) != float(last) and float(order_price) not in buy_list:
                    # print('Last price is: {} and order price is: {}. Adding to buy list.'.format(last, order_price))
                    buy_list.append(order_price)
                elif float(order_price) >= float(price_list[minute]) and float(order_price) != float(last) and float(order_price) not in sell_list:
                    # print('Last price is: {} and order price is: {}. Adding to sell list.'.format(last, order_price))
                    sell_list.append(order_price)
                    
        else:
            for order_price in low_orders:
                if float(order_price) < float(price_list[minute]) and float(order_price) != float(last) and float(order_price) not in buy_list:
                    # print('Last price is: {} and order price is: {}. Adding to buy list.'.format(last, order_price))
                    buy_list.append(order_price)
            
            for order_price in high_orders:
                if float(order_price) >= float(price_list[minute]) and float(order_price) != float(last) and float(order_price) not in sell_list:
                    # print('Last price is: {} and order price is: {}. Adding to sell list.'.format(last, order_price))
                    sell_list.append(order_price)
        
    buy_list.sort()
    sell_list.sort()
            
    return buy_list, sell_list

def execute_grid(df, minutes, ticker, ticker2, spread, orders, investment, period=0, deviations=0):
        
    t1_price_list = df[ticker][-minutes:].to_list()
    
    if ticker2 == 'USDT':
        t2_price_list = [1 for x in range(len(t1_price_list))]
        price_list = t1_price_list
        t2_amount = investment/2
    else:
        t2_price_list = df[ticker2][-minutes:].to_list()
        t2_amount = (investment/2) / t2_price_list[0]
        
        ratio_price_list = []
        for i in range(len(t1_price_list)):
            t1 = t1_price_list[i]
            t2 = t2_price_list[i]
            ratio_price_list.append(t1/t2)
            
        price_list = ratio_price_list

    t1_amount = (investment/2) / t1_price_list[0]

    t1_per_order = math.floor(t1_amount/(orders/2))

    start_price = t1_price_list[0]

    reach = spread/2
    bottom = price_list[0] * (1 - (reach/100))
    top = price_list[0] * (1 + (reach/100))
    difference = top - bottom
    interval = difference/(orders-1)
    last_index = {'buy': None, 'sell': None}
    
    if period > 0:
        order_list = [low_roller, high_roller] = get_ma_list(df, minutes, ticker, ticker2, period, deviations)
        buy_list, sell_list = reset_order_lists(order_list, price_list, 0, orders, spread=spread, period=period, last_index=last_index)
    else:
        order_list = [(x * interval) + bottom for x in range(orders)]
        buy_list, sell_list = reset_order_lists(order_list, price_list, 0, 0)
            
    minute = 0
    buy_transaction_list = []
    sell_transaction_list = []
    last = 0
    # print('Starting loop...')
    
    while minute < len(price_list):
        if period <= 0:
            buy_list, sell_list = reset_order_lists(order_list, price_list, minute, orders, buy_list, sell_list, last)
        if period > 0:
            buy_list, sell_list = reset_order_lists(order_list, price_list, minute, orders, buy_list, sell_list, last, spread, period, last_index)
        price = price_list[minute]
        if 1 <= len(sell_list) and 1 <= len(buy_list):
            while float(buy_list[-1]) >= float(price) and t2_amount >= t1_per_order * buy_list[-1]:
                # print("Current price: {} is less than buy offer: {}. Executing purchase.".format(price, buy_list[-1]))
                last_index['buy'] = len(buy_list)-1
                bought = float(buy_list.pop(-1))
                transaction = {'price': bought, 'minute': minute}
                buy_transaction_list.append(transaction)
                last = float(bought)
                
                sell_list.sort()
                
                # print("buying {} of {} at {} for {}".format(t1_per_order, ticker, bought, t1_per_order*bought))
                t1_amount = t1_amount + (t1_per_order * 0.9992)
                t2_amount = t2_amount - (t1_per_order*bought)
                
                if len(buy_list) == 0:
                    break
                
            while float(sell_list[0]) <= float(price) and float(t1_amount) >= float(t1_per_order):
                last_index['sell'] = (orders/2) - len(sell_list)-1
                # print("Current price: {} is greater than sell offer: {}. Executing sale.".format(price, sell_list[0]))
                sold = float(sell_list.pop(0))
                transaction = {'price': sold, 'minute': minute}
                sell_transaction_list.append(transaction)
                last = float(sold)
                
                buy_list.sort()
                
                t2_amount = t2_amount + ((t1_per_order * sold) * 0.9992)
                t1_amount = t1_amount - t1_per_order
                
                if len(sell_list) == 0:
                    break
                
            minute += 1

        if 1 > len(sell_list):
            try:
                while float(buy_list[-1]) >= float(price) and t2_amount >= t1_per_order * buy_list[-1]:
                    last_index['buy'] = len(buy_list)-1
                    # print("BUYING ONLY! SELL LIST IS GONE.")
                    # print('Current price: {} is greater than buy price: {}, executing purchase.'.format(price, buy_list[-1]))
                    # print('t1_amount: {}'.format(t1_amount))
                    # print('t2_amount: {}'.format(t2_amount))
                    bought = float(buy_list.pop(-1))
                    transaction = {'price': bought, 'minute': minute}
                    buy_transaction_list.append(transaction)
                    last = bought

                    sell_list.sort()

                    t1_amount += (t1_per_order * 0.9992)
                    t2_amount -= (t1_per_order * bought)
            except:
                # print('Buy list length error, check next loop. Should not get 2 of these in a row.')
                minute += 1
                continue

            minute += 1
            continue

        if 1 > len(buy_list):
            try:
                while float(sell_list[0]) < float(price) and t1_amount >= t1_per_order:
                    last_index['sell'] = (orders/2) - len(sell_list)-1
                    # print("SELLING ONLY! BUY LIST IS GONE.")
                    # print('Current price: {} is less than sell price: {}, executing purchase.'.format(price, sell_list[-1]))
                    sold = float(sell_list.pop(0))
                    transaction = {'price': sold, 'minute': minute}
                    sell_transaction_list.append(transaction)
                    last = sold

                    buy_list.sort()

                    t2_amount = t2_amount + ((t1_per_order * sold) * 0.9992)
                    t1_amount = t1_amount - t1_per_order
            except:
                # print('Sell list length error, check next loop. Should not get 2 of these in a row.')
                minute += 1
                continue
            
            minute += 1
            continue
                
    t1_value = t1_price_list[-1] * t1_amount
    t2_value = t2_price_list[-1] * t2_amount
    final_value = t1_value + t2_value
    # print('t1_value: {}'.format(t1_value))
    # print('t2_value: {}'.format(t2_value))
    # print("Finished after iterating through {} minutes. If this value isn't equal to: {}, an error occurred.".format(minute, minutes))
    
    t1_hodl = ((investment/2) / t1_price_list[0]) * t1_price_list[-1]
    t2_hodl = ((investment/2) / t2_price_list[0]) * t2_price_list[-1]
    
    hodl_value = t1_hodl + t2_hodl
    
    # print('')
    # print("##########################################################################")
    # print('')
    # print("Final value is: {}. Hold value is: {}. Net gain is {} ({})% over {} minutes, or {} days.".format(round(final_value, 2), round(hodl_value, 2), round(final_value-hodl_value, 2), round(((final_value-hodl_value)/hodl_value) *100, 2), minutes, round(minutes/1444, 2)))
    
    return t1_amount, t2_amount, final_value, buy_transaction_list, sell_transaction_list