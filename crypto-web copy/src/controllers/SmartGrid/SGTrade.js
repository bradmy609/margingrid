import { useState, useEffect } from 'react';
import { ExecuteGrid } from './ExecuteGrid';

export function SGTrade(props) {
    let defaultIndex = props.tickers.indexOf('AVAX');
    if (defaultIndex === -1) {
        defaultIndex = props.tickers.indexOf('ETH');
    }
    const [tradeSettings, setTradeSettings] = useState({orders: 30, spread: 50, ticker: props.tickers[defaultIndex], updateFrequency:Math.round(props.settings.minutes/30), period:props.settings.minutes/10, gridType:'dynamic',
    maInd: true, fillBot:true, repeatSells:true, repeatBuys:true})

    function handleChange(e) {
        const name = e.target.name;
        let value = e.target.value;
        const prevValue = tradeSettings[name];
        if (prevValue === true || prevValue === false) { 
            value = !prevValue;
        }
        setTradeSettings(tradeSettings => {
            const newSettings = {...tradeSettings}
            newSettings[name] = value;
            return newSettings;
        });
    };

    useEffect(() => {
        let newOrders
        let newSpread
        if (props.settings.base === 'BTC') {
            newSpread = 30;
            newOrders = 50;
        } else {
            newSpread = 80;
            newOrders = 50;
        }
        setTradeSettings(tradeSettings => {
            const newSettings = {...tradeSettings};
            newSettings.orders = newOrders;
            newSettings.spread = newSpread;
            return newSettings;
        })
    }, [props.settings.base]);

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
            <form className='SGForm'>
                    <h2>Configure Trading Grid</h2>
                    <table className='inputTable'>
                        <tbody>
                            <tr>
                                <td><label>Trade Ticker</label></td>
                                <td>
                                    <select name='ticker' value={tradeSettings.ticker} onChange={handleChange} className='tickerSelect'>
                                        {options}
                                    </select>
                                </td>
                            </tr>
                            <tr>
                                <td><label>Grid Type</label></td>
                                <td>
                                    <select name='gridType' onChange={handleChange} value={tradeSettings.gridType}>
                                        <option value='static'>
                                            Static
                                        </option>
                                        <option value='dynamic'>
                                            Dynamic
                                        </option>
                                    </select>
                                </td>
                            </tr>
                            <tr>
                                <td><label>Order Quantity</label></td>
                                <td><input type='number' name='orders' max='100' min='2' step='2' value={tradeSettings.orders} onChange={handleChange} className='SGInput' /></td>
                            </tr>
                            <tr>
                                <td><label>Spread (Max 200)</label></td>
                                <td><input type='number' name='spread' max='200' min='1' value={tradeSettings.spread} onChange={handleChange} className='SGInput' /></td>
                            </tr>
                            <tr>
                                <td><label>Update Frequency (minutes)</label></td>
                                <td><input type='number' name='updateFrequency' max='10000' min='1' step='10' value={tradeSettings.updateFrequency} onChange={handleChange} /></td>
                            </tr>
                            <tr>
                                <td><label>Moving Average Period (minutes)</label></td>
                                <td><input type='number' name='period' max='10000' step='10' value={tradeSettings.period} onChange={handleChange} /></td>
                            </tr>
                            <tr>
                                <td><label>Use Moving Average Indicator?</label></td>
                                <td><input name='maInd' type='checkbox' value={tradeSettings.maInd} onChange={handleChange} defaultChecked={true}/></td>
                            </tr>
                            <tr>
                                <td><label>Fill Selling Orders from Bottom?</label></td>
                                <td><input name='fillBot' type='checkbox' value={tradeSettings.fillBot} onChange={handleChange} defaultChecked={true}/></td>
                            </tr>
                            <tr>
                                <td><label>Repeat Selling Orders?</label></td>
                                <td><input name='repeatSells' type='checkbox' value={tradeSettings.repeatSells} onChange={handleChange} defaultChecked={true}/></td>
                            </tr>
                            <tr>
                                <td><label>Repeat Buying Orders?</label></td>
                                <td><input name='repeatBuys' type='checkbox' value={tradeSettings.repeatBuys} onChange={handleChange} defaultChecked={true}/></td>
                            </tr>
                        </tbody>
                </table>
            </form>
            {<ExecuteGrid settings={props.settings} borrowSettings={props.borrowSettings} tradeSettings={tradeSettings}/>}
        </>
        )
}