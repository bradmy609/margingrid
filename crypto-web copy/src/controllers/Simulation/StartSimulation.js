import {useState} from "react";
import {BorrowInput} from "./Borrow/BorrowInput";
import { TradeInputs } from "./Trade/TradeInputs";
import { PandasTable } from "../../helpers/PandasTable";

export function StartSimulation(props) {
    const [investment, setInvestment] = useState(1000);
    const [showInput, setShowInput] = useState(true);
    const [minutes, setMinutes] = useState(10000);
    const [leverage, setLeverage] = useState(10);
    const [table, setTable] = useState('');
    const [sum, setSum] = useState(100);

    const [borrowData, setBorrowData] = useState(null);

    function upStream(stuff) {
        setBorrowData(stuff);
    }
    
    function upStreamTable(stuff) {
        setTable(stuff);
    }

    function streamSum(stuff) {
        setSum(stuff);
    }

    function handleChange(e) {
        setMinutes(e.target.value);
    }

    const borrowTable = borrowData && table ? (
        <div>
            <h3>Borrowed Coins:</h3>
            <PandasTable html={table} />
        </div>
        ) : null

    return (
    <div>
        {showInput ? (
        <>
            <div className='borrowForm'>
                <table>
                    <tbody>
                        <tr>
                            <td>Set Investment Amount ($)</td>
                            <td><input type="number" max="1000000" min="100" step="100" name="investment" defaultValue="1000" onChange={(e) => setInvestment(e.target.value)}></input></td>
                        </tr>
                        <tr>
                            <td>How many minutes of data to back-test?</td>
                            <td><input className="minutes" type="number" name="minutes" min="1" max={props.length-1} value={minutes} onChange={handleChange}></input></td>
                        </tr>
                        <tr>
                            <td>Leverage</td>
                            <td><input type="number" defaultValue="10" onChange={(e) => setLeverage(e.target.value)} max="10" min="0"/></td>
                        </tr>
                    </tbody>
                </table>        
            </div>
            <button className="saveAndContinue" onClick={() => setShowInput(false)}>Save and Continue</button>
        </>
        ) : (
            <div>
                <div className="simulationDiv">
                    <h2>Simulation Data</h2>
                    <h3 className="simulationText">Margin Account Portfolio Balance:</h3><h3 className="inputText">${investment * leverage}</h3>
                    <h3 className="simulationText">Back-Test Simulating Grid Trading Over:</h3><h3 className="inputText">{minutes} Minutes</h3>
                    {borrowTable}
                </div>
            {props.tickers ? <BorrowInput minutes={minutes} investment={investment} leverage={leverage} tickers={props.tickers} upStream={upStream} table={upStreamTable} streamSum={streamSum}/> : null}
            </div>
        )
        }
        {borrowData && props.tickers? (
        <div>            
            <TradeInputs tickers={props.tickers} sum={sum} table={table} minutes={minutes} start_investment={investment} investment={investment * leverage} borrowData={borrowData}/>
        </div>
        ) : null}
    </div>
    )
}
