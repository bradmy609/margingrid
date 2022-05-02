import {useEffect, useState, useCallback} from "react";
import { QuerySimulation } from "./querySimulation/QuerySimulation";

export function TradeInputs(props){
    // const [quantity, setQuantity] = useState(1);
    const [selections, setSelections] = useState([{name: props.tickers[0],  percent: 10, orders:20, spread: 30, period: 300, std: 1}]);
    const [totalPercent, setTotalPercent] = useState(0);
    const [finish, setFinish] = useState(false);
    const [labels, setLabels] = useState(null);
    const [allPercent, setAllPercent] = useState(10);

    function handleStateChange(e) {
        const index = e.target.id;
        const value = e.target.value;
        const name = e.target.name;
        setSelections(selections => {
            const items = [...selections];
            const item = items[index];
            item[name] = value;
            items[index] = item;
            return items;
        })
    }

    const buildOptions = useCallback((index) => {
        const options = props.tickers.map(ticker => {
            return (
                <option key={ticker+index} value={ticker}>{ticker}</option>
            )
        });
        return options;
    }, [props.tickers]);

    useEffect(() => {
        if (selections) {
        setTotalPercent(selections.reduce((prev, curr) => {
            return Number(prev)+Number(curr.percent)
        }, 0))
    }
    }, [selections]);

    const createLabels = useCallback((quantity) => {
        const arr = [...Array(quantity).keys()];
        return arr.map((num, index) => {
            return  (
                <tr key={"selectForm" + num.toString()}>
                    <td>
                        <select key={"select" + index.toString() + num} name="name" id={index} onChange={handleStateChange} value={selections[index].name}>
                            {props.tickers ? buildOptions(index) : null}
                        </select>
                    </td>
                    <td>
                        <input key={index} id={index} name="percent" type="number" min="5" step="5" max={selections ? (100-(totalPercent-selections[index].percent)) : 100} onChange={handleStateChange} value={selections[index].percent}></input>
                    </td>
                    <td>
                        <input type="number" id={index} name="orders" min="2" max="100" onChange={handleStateChange} value={selections[index].orders}/>
                    </td>
                    <td>
                        <input type="number" id={index} name="spread" min="4" max="100" onChange={handleStateChange} value={selections[index].spread}/>
                    </td>
                    <td>
                        <input type="number" id={index} name="period" min="2" max={props.length} onChange={handleStateChange} value={selections[index].period}/>
                    </td>
                    <td>
                        <input type="number" id={index} name="std" min="1" max="10" onChange={handleStateChange} value={selections[index].std}/>
                    </td>
                </tr>
                )
        })
    }, [selections, buildOptions, props.tickers, totalPercent, props.length]);

    function onChange(e) {
        const arr = [...Array(Number(e.target.value)).keys()];
        const res = arr.map((ele, index) => {
            return {name: props.tickers[props.tickers.length - index - 1], percent: allPercent, orders: 20, spread: 30, period: 300, std: 1}
        })
        if (res.length > selections.length) {
            setSelections(selections => {
                const newRes = res.slice(selections.length)
                return [...selections, ...newRes];
            })
        }
        else {
            setSelections(selections => {
                const newRes = selections.slice(0, res.length)
                return newRes;
            });
        }
    }

    function onSubmit(e) {
        e.preventDefault();
        setFinish(true);
    };

    useEffect(() => {
        const tableInputs = (
            <>
                <table>
                    <thead>
                        <tr>
                            <th><label>Ticker</label></th>
                            <th><label>MA Standard Deviations</label></th>
                            <th><label>Orders</label></th>
                            <th><label>Price Spread (%)</label></th>
                            <th><label>MA Window(Minutes)</label></th>
                            <th><label>MA Standard Deviations</label></th>
                        </tr>
                    </thead>
                    <tbody>
                        {createLabels(selections.length)}
                    </tbody>
                </table>
            </>
        )
        setLabels(tableInputs);
    }, [selections, createLabels]);

    function handleAllChange(e) {
        const value = e.target.value;
        const name = e.target.name;
        if (name === 'percent') {
            setAllPercent(value);
        }
        const newSelections = selections.map(ele => {
            ele[name] = value;
            return ele;
        })
        setSelections(newSelections);
    }

    return (
        <div>
            <h1>Select Currencies to Trade</h1>
            {finish ? (
            <div>
                <QuerySimulation start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={selections} borrowData={props.borrowData} />
                <button onClick={()=>setFinish(false)}>Re-Configure Trades</button>
            </div>
            ) : (
            <div>
                <h3>{totalPercent ? `Portfolio Percent ${totalPercent}% Must Equal ${props.sum}%`: null}</h3>
                <label><h2>Input # of Currencies to Trade: </h2></label>
                <input type="number" min="1" max={Math.round((100-totalPercent)/10) + selections.length} defaultValue="1" onChange={onChange}/>
                <br/>
                <h4>
                    <label>Change ALL Percent</label>
                    <input className="quantity" type="number" name="percent" onChange={handleAllChange} min="5" max={Math.floor(100/selections.length)} step="5" value={allPercent} />
                    <label>Change All Orders</label>
                    <input type="number" name="orders" onChange={handleAllChange} min="4" max="100" defaultValue="20"/>
                    <label>Change All Spread</label>
                    <input type="number" name="spread" onChange={handleAllChange} min="4" max="100" defaultValue="30"/>
                    <label>Change ALL Window</label>
                    <input type="number" name="period" onChange={handleAllChange} min="4" max={props.length} defaultValue="300" />
                    <label>Change ALL Standard Deviations</label>
                    <input type="number" name="std" onChange={handleAllChange} min="1" max="10" defaultValue="1" />
                </h4>
                <br/>
                {labels ? labels : null}
                <input disabled={props.sum !== totalPercent} type="submit" value="Submit" onClick={onSubmit}/>
            </div>
            )
        }
        </div>
    )
}