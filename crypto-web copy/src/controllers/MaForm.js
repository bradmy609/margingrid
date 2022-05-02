import {useState} from "react";
import {DataTable} from "./MaDataTable";
import {TestChart} from "../helpers/testChart";
import {apiPath} from "../apiPath";


export function MaForm(props) {
    const [data, setData] = useState();

    async function onSubmit(e) {
        e.preventDefault();
        const ticker = e.target.ticker.value;
        const period = e.target.period.value;
        const quantity = e.target.quantity.value;

        try{
            const response = await fetch(`${apiPath}/api/ma/${ticker}/${period}/${quantity}`);
            if (response.ok) {
                const jsonRes = await response.json();
                setData(jsonRes);
            }
        } catch(e) {
            console.log(e);
        }
    }

    function buildOptions() {
        const options = props.tickers.map((ticker, index) => {
            return (
                <option key={ticker+index} value={ticker}>{ticker}</option>
            )
        });
        return options;
    }

    return (
        <div>
            <form name="maForm" onSubmit={onSubmit}>
                <label>Ticker:
                    <select name="ticker" id='maTicker' type="text" defaultValue="ETH">
                        {props.tickers ? buildOptions() : null}
                    </select>
                </label>
                <br/>
                <label>Period:
                    <input name="period" type="number" defaultValue="30" />
                </label>
                <br/>
                <label>Quantity:
                    <input name="quantity" type="number" defaultValue="10" />
                </label>
                <br/>
                    <input name="submit" type="submit"/>
                    <input name="reset" type="reset" onClick={(e) => setData(null)} />
            </form>
            {data ? <DataTable ticker={Object.keys(data)} data={Object.values(data)}/> : null}
            {data ? <TestChart ticker={Object.keys(data)} data={Object.values(data)}/> : null}
        </div>
    )
}
