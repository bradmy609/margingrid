import { useEffect, useState } from 'react';
import { SGTrade } from './SGTrade'
// orders, spread, ticker, percent, market_sell=True, only_above=True, period=1000, grid_type='static'

export function SGBorrow(props) {
    let defaultIndex = props.tickers.indexOf('BNB');
    if (defaultIndex === -1) {
        defaultIndex = props.tickers.indexOf('ATOM');
    }
    const [borrowSettings, setBorrowSettings] = useState({orders: 20, spread: 20, ticker: props.tickers[defaultIndex], marketSell:false, onlySellAbove:true, period:5000, gridType:'static'})

    useEffect(() => {
        let newVal
        props.settings.base === 'BTC' ? newVal = 20 : newVal = 60;
        setBorrowSettings(borrowSettings => {
            const newSettings = {...borrowSettings};
            newSettings.orders = newVal;
            newSettings.spread = newVal;
            return newSettings;
        })
    }, [props.settings.base]);

    function handleChange(e) {
        const name = e.target.name;
        let value = e.target.value;
        const prevValue = borrowSettings[name];
        if (prevValue === true || prevValue === false) { 
            value = !prevValue;
        }
        setBorrowSettings(borrowSettings => {
            const newSettings = {...borrowSettings}
            newSettings[name] = value;
            return newSettings;
        })
    }

    const options = props.settings.base !== 'BTC' ? props.tickers.map(ele => {
                    return <option key={ele}value={ele}>{ele}</option>
                    }) : props.tickers.map(ele => {
                        if (ele !== 'BTC') {
                            return <option key={ele}value={ele}>{ele}</option>
                        } else {
                            return null;
                        };
                    });

    return (
        <>
            <form className='SGForm' >
                <h2>Configure Selling Grid</h2>
                <table className='inputTable'>
                    <tbody>
                        <tr>
                            <td><label>Short Ticker</label></td>
                            <td>
                                <select name='ticker' value={borrowSettings.ticker} onChange={handleChange} className='tickerSelect'>
                                    {options}
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td><label>Order Quantity</label></td>
                            <td><input type='number' name='orders' max='100' min='2' value={borrowSettings.orders} onChange={handleChange} className='SGInput' /></td>
                        </tr>
                        <tr>
                            <td><label>Spread (Max 200)</label></td>
                            <td><input type='number' name='spread' max='200' min='1' value={borrowSettings.spread} onChange={handleChange} className='SGInput' /></td>
                        </tr>
                        <tr>
                            <td><label>Moving Average Period (minutes)</label></td>
                            <td><input type='number' name='period' max='10000' min='2' value={borrowSettings.period} onChange={handleChange} defaultChecked={borrowSettings.period}/></td>
                        </tr>
                        <tr>
                            <td><label>Sell at Market Price Upon Start?</label></td>
                            <td><input name='marketSell' type='checkbox' value={borrowSettings.marketSell} onChange={handleChange}/></td>
                        </tr>
                        <tr>
                            <td><label>Only Sell Above Market Price?</label></td>
                            <td><input name='onlySellAbove' type='checkbox' value={borrowSettings.onlySellAbove} onChange={handleChange} defaultChecked={true}/></td>
                        </tr>
                    </tbody>
                </table>
            </form>
                <SGTrade tickers={props.tickers} settings={props.settings} borrowSettings={borrowSettings} />
        </>
        )
}