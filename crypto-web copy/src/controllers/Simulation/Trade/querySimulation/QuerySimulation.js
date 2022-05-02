import {useState, useEffect} from "react";
//import { USDTGrid } from "./USDTGrid";
import { getData } from "../../../../helpers/postFunction";
import { apiPath } from "../../../../apiPath";
import { MaBTCGrid } from "./MaBTCGrid";
import { MaETHGrid } from "./MaETHGrid";
import { MaUSDTGrid } from "./MaUSDTGrid";
import { ETHGrid } from "./ETHGrid";
import { BTCGrid } from "./BTCGrid";
import { USDTGrid } from "./USDTGrid";

export function QuerySimulation(props) {
    const [borrowData, setBorrowData] = useState("Loading...");
    const [tradeData, setTradeData] = useState("Loading...");
    const [toggleTables, setToggleTables] = useState("Show");
    const [debt, setDebt] = useState(null);
    const [staticComplete, setStaticComplete] = useState(false);

    useEffect(() => {
        async function postReq() {
            const url = `${apiPath}/api/hodl/${props.minutes}/${props.investment}`;
            const response = await getData(url, props.borrowData);
            if (response) {
                setBorrowData(response)
            } else {
                console.log("Response object does not exist!");
            }
            const tradeResponse = await getData(url, props.data);
            if (response) {
                setTradeData(tradeResponse);
            } else {
                console.log("Response object does not exist!");
            }
        }
        postReq();
    }, [props.borrowData, props.investment, props.minutes, props.data]);

    function downstream(stuff) {
        setStaticComplete(stuff);
    }

    function handleClick() {
        setToggleTables(toggleTables => {
            if (toggleTables === 'Show') {
                return 'Hide';
            } else if (toggleTables === 'Hide') {
                return 'Show';
            }
        })
    };

    async function setDebtValue() {
            const borrowedValue = await Math.round(borrowData['total']*100)/100 
            setDebt(Math.round((borrowedValue - props.start_investment)*100)/100)
    }

    if (borrowData !== 'Loading...') {
        setDebtValue();
    }
    
    const hodlAssets = Math.round(tradeData['total']*100)/100
    const hodlProfit = Math.round((hodlAssets - debt - props.start_investment)*100)/100;
    const hodlFinal = Math.round((props.start_investment + hodlProfit) * 100)/100;

    return (
        <div>
            <br/>
            <div className='HODLresultsDiv'>
                <h1>HODL Results</h1>
                {tradeData ? (
                    <div>
                        <h3>Start Value: ${props.start_investment}</h3>
                        <h3>Total Assets: ${hodlAssets ? hodlAssets : "Loading..."}</h3>
                        <h3>Total Debt: ${debt ? debt : "Loading..."}</h3>
                        <h3>Final Value: ${hodlFinal}</h3>
                        <h2>Profit: ${hodlProfit}</h2>
                        <h2>Profit Per Day: ${Math.round((1444/props.minutes)*hodlProfit*100)/100}</h2>
                        {tradeData ?  <div dangerouslySetInnerHTML = {{__html: tradeData['html']}}></div> : 'Loading Table...'}
                    </div>
                    ) : tradeData}
            </div>
            <div className="resultDiv">
                <USDTGrid start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={props.data} debt={debt} upstream={downstream}/>
                <BTCGrid start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={props.data} debt={debt} />
                <ETHGrid start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={props.data} debt={debt} />
                {/* <KCSGrid start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={props.data} debt={debt} upstream={downstream}/> */}
                {/* {tradeData ? <USDTGrid start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={props.data} debt={debt} complete={downstream}/> : null} */}
            </div>
            {staticComplete ? (
                <div>
                    <div>
                        <MaBTCGrid start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={props.data} debt={debt}/>
                        <MaETHGrid start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={props.data} debt={debt} />
                        {/* <MaKCSGrid start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={props.data} debt={debt} /> */}
                        <MaUSDTGrid start_investment={props.start_investment} minutes={props.minutes} investment={props.investment} data={props.data} debt={debt} />
                    </div>
                </div>
            ) : "Loading MA Grids..."}
            <br/>
            <button onClick={handleClick}>{toggleTables} Borrow Results</button>
            {toggleTables === 'Hide' ? (
                <div>
                    <h2>Borrow Table</h2>
                    {borrowData ?  <div dangerouslySetInnerHTML = {{__html: borrowData['html']}}></div> : 'Loading Table...'}
                </div>
            ) : null}
        </div>
    )
}