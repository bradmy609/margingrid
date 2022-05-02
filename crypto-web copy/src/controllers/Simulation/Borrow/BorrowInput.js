import {useEffect, useState, useCallback} from "react";
import {Query} from "./SubmitQuery/Query";

export function BorrowInput(props) {
    const [sum, setSum] = useState(null);
    const [finished, setFinished] = useState(false);
    const [list, setList] = useState([{'name': props.tickers[0], 'percent': 10}]);
    const [allPercent, setAllPercent] = useState(10);
    const [unusedTickers, setUnusedTickers] = useState(props.tickers);

    function onChange(e) {
        const arr = [...Array(Number(e.target.value)).keys()];
        const res = arr.map((ele, index) => {
            return {name: props.tickers[index], percent: allPercent}
        })
        if (res.length > list.length) {
            setList(list => {
                const newRes = res.slice(list.length)
                return [...list, ...newRes];
            })
        }
        else {
            setList(list => {
                const newRes = list.slice(0, res.length)
                return newRes;
            });
        }
    }

function setVal(e) {
    const id = e.target.id;
    const val = e.target.value;
    const name = e.target.name;
    setList(list => {
        let items = [...list];
        let item = items[id];
        item[name] = val;
        items[id] = item;
        return items;
    });
}

    const inputs = useCallback(() => {
        function buildOptions(index) {
            const options = props.tickers.map(ticker => {
                return (
                    <option key={ticker+index} value={ticker}>{ticker}</option>
                )
            });
            return options;
        }
        const arr = [...Array(list.length).keys()];
        return arr.map((num, index) => {
            return  (
                <div key={"divForm" + num.toString()}>
                    <label htmlFor="tickers"><h5 style={{display: "inline-block", padding: 6}}>{index+1}. </h5>Choose a Ticker to Borrow</label>
                    <select key={"select" + index.toString()} name='name' id={index} onChange={setVal} value={list[index].name} style={{width: 75}}>
                        {props.tickers ? buildOptions(index) : null}
                    </select>
                    <label htmlFor="portfolioPercent">Percent of Portfolio:</label>
                    <input key={index} id={index} name="percent" type="number" min="1" max={100} step="1" value={list[index].percent} onChange={setVal}></input>
                </div>
            )
        })
    }, [list, props.tickers]);

    function handleSubmit(e) {
        e.preventDefault();
        props.streamSum(sum);
        setFinished(true);
    }

    useEffect(() => {
        setSum(list.reduce((prev, curr) => Number(prev)+Number(curr.percent), 0))
        const usedTickers = list.map(ele => ele.name);
        setUnusedTickers(props.tickers.filter(ele => !usedTickers.includes(ele)))
    }, [list, props.tickers]);

    function handleAllChange(e) {
        const value = e.target.value;
        const name = e.target.name;
        if (name === 'percent') {
            setAllPercent(value);
        }
        const newList = list.map(ele => {
            ele[name] = value;
            return ele;
        })
        setList(newList);
    }

    function getRandom() {
        let allTickers = props.tickers;
        setList(list => {
            return list.map(ele => {
                const ticker = allTickers[Math.floor(Math.random()*allTickers.length)];
                allTickers = allTickers.filter(ele => ele !== ticker);
                setUnusedTickers(allTickers);
                return {...ele, name: ticker};
            })
        })
    }

    return (
    <>
        {finished ? (
        <>
            <Query investment={props.investment} leverage={props.leverage} minutes={props.minutes} data={list} upStream={props.upStream} table={props.table}/>
        </>
        ) : (
        <div className="borrowForm">
            <h1>Borrowing</h1>
            <h3>{`${sum}% Portfolio Used`}</h3>
            <label>Input # of Currencies to Borrow<input type="number" defaultValue="1" onClick={onChange} min="1" max={unusedTickers.length} /></label>
            <br/>
            {sum > 100 ? <h3 style={{color: 'red'}}>Please reduce portfolio percent to 100% or below in order to continue.</h3> : null}
            <button onClick={getRandom}>Randomly Select Coins</button>
            <label>Set ALL Percent <input type="number" name="percent" min="1" max={Math.floor(100/list.length)} value={allPercent} onChange={handleAllChange}/></label>
            <form onSubmit={handleSubmit}>
                {props.tickers ? inputs() : null}
                <input type="submit" disabled={sum > 100}></input>
            </form>
        </div>
        )
        }
    </>
    )
}
