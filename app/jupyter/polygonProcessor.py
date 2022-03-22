#!/usr/bin/env python
# coding: utf-8

# In[43]:


import requests
import pandas as pd


# In[15]:


grouped_daily = requests.get('https://api.polygon.io/v2/aggs/grouped/locale/global/market/crypto/2022-02-17?adjusted=true&apiKey=81oGdC78et6jp5itDXcGQRqkK4FtPdmX')


# In[17]:


gd_results = grouped_daily.json()['results']
pairs = [obj['T'].replace('X:', '') for obj in gd_results]
all_tickers = [x[0:-3] for x in pairs]
tickers = list(set(all_tickers))


# In[321]:


def get_max_data(ticker):
    data = {}
    data[ticker] = {}
    try:
        res = requests.get('https://api.polygon.io/v2/aggs/ticker/X:{ticker}USD/range/1/minute/2021-11-22/2021-12-27?adjusted=true&sort=asc&limit=50000&apiKey=81oGdC78et6jp5itDXcGQRqkK4FtPdmX'.format(ticker=ticker)).json()
        res_results = res['results']
        for key in res_results[0].keys():
            data[ticker][key] = [x[key] for x in res_results]
    except Exception as e:
        print(e)
        print(res)
    return data


# In[322]:


def get_all_max(ticker_list):
    lst = []
    for ticker in ticker_list:
        res = get_max_data(ticker)
        lst.append(res)
    return lst


# In[323]:


tickers.sort()


# In[324]:


tickers_slice = tickers[:5]


# In[326]:


top_five = ['BTC', 'ETH', '1INCH', 'AAVE', 'MATIC']


# In[327]:


top_lst = get_all_max(top_five)


# In[371]:


def build_dfs(res_lst):
    v, vw, o, c, l, h, t = {}, {}, {}, {}, {}, {}, []
    index = []
    for count, obj in enumerate(res_lst):
        ticker = list(obj.keys())[0]
        for x in obj.values():
            for key, vals in x.items():
                if len(vals) < 50000:
                    diff = 50000 - len(vals)
                    vals.extend([None for x in range(diff)])
                if key == 'v':
                    v[ticker] = vals
                elif key == 'vw':
                    vw[ticker] = vals
                elif key == 'o':
                    o[ticker] = vals
                elif key == 'c':
                    c[ticker] = vals
                elif key == 'l':
                    l[ticker] = vals
                elif key == 'h':
                    h[ticker] = vals
                elif key == 't' and len(t) == 0 and len(vals) >= 50000:
                    t = pd.Series(vals)*1000000

    index = [x for x in range(50000)]
    dt_index = pd.DatetimeIndex(t)
    multi_dex = pd.MultiIndex.from_tuples(zip(index, dt_index), names=['index', 'datetime'])

    vdf = pd.DataFrame(v, index=multi_dex).loc[:48960]
    vwdf = pd.DataFrame(vw, index=multi_dex).loc[:48960]
    odf = pd.DataFrame(o, index=multi_dex).loc[:48960]
    cdf = pd.DataFrame(c, index=multi_dex).loc[:48960]
    hdf = pd.DataFrame(h, index=multi_dex).loc[:48960]
    ldf = pd.DataFrame(l, index=multi_dex).loc[:48960]

    dfs = {'v': vdf, 'vw': vwdf, 'o': odf, 'c': cdf, 'h': hdf, 'l': ldf}
    return dfs


# In[374]:


dfs = build_dfs(top_lst)


# In[ ]:




