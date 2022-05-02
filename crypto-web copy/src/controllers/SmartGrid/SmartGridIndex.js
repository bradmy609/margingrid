import { useState } from 'react';
import { SGBorrow } from './SGBorrow';
import './SmartGridBorrow.css'

export function SmartGrid(props) {
    const [settings, setSettings] = useState({'investment': 1000, 'minutes': Math.round(props.length/50000)*10000, offset: 0, base: 'BTC'});
    
    function handleChange(e) {
        const name = e.target.name;
        const value = e.target.value;
        setSettings(settings => {
            const oldSettings = {...settings}
            oldSettings[name] = value;
            return oldSettings;
        })
    }

    const description = `The smart grid is a dual-volatility-trading-grid-system that utilizes algorithms to profit from small volatility while minimizing risks.
    You select one coin to incrementally open a leveraged short position on. You select a second coin to trade with, profiting from it's volatility.`

    return (
        <>
            <p className='description'>{description}</p>
            <div className='SGForm'>
                    <h1>Investment and Duration</h1>
                    <table className='inputTable'>
                        <tbody>
                            <tr>
                                <td><label>Investment</label></td>
                                <td><input type='number' max='1000000' name='investment' value={settings.investment} onChange={handleChange} className='SGInput' size='50'/></td>
                            </tr>
                            <tr>
                                <td><label>How many minutes to back-test?</label></td>
                                <td><input type='number' max={props.length-settings.offset} name='minutes' value={settings.minutes} onChange={handleChange} className='SGInput' /></td>
                            </tr>
                            <tr>
                                <td><label>Minutes Offset <p id='parenthesis'>(How many minutes to remove from the end of DB before backtesting?)</p></label></td>
                                <td><input type='number' max={props.length-settings.minutes} value={settings.offset} onChange={handleChange} name='offset'></input></td>
                            </tr>
                            <tr>
                                <td>
                                    <label>Base Coin</label>
                                </td>
                                <td>
                                    <select onChange={handleChange} value={settings.base} name='base'>
                                        <option value='BTC'>BTC</option>
                                        <option value='USDT'>USDT</option>
                                    </select>
                                </td>
                            </tr>
                        </tbody>
                    </table>
            </div>
            <SGBorrow tickers={props.tickers} settings={settings}/>
            <br/>
        </>
    )
}