import { useEffect, useState } from 'react';
import {apiPath} from '../../apiPath';
import { getData } from '../../helpers/postFunction';
import { PandasTable } from '../../helpers/PandasTable';
import { LineChart } from '../../helpers/lineChart';

export function ExecuteGrid(props){
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(null);

    const resetLoading = () => {
        setLoading('Loading Results...');
    }

    const handleClick = () => {
        resetLoading();
        const data = {settings: props.settings, borrowSettings: props.borrowSettings, tradeSettings: props.tradeSettings};
        const URL = `${apiPath}/api/grid/smart/${props.settings.minutes}/${props.settings.investment}`;
        async function fetchData() {
            const response = await getData(URL, data)
            if (response) {
                setResults(response);
            } else {
                console.log("Smart Grid does not exist.")
            }
        }
        fetchData();
    };

    useEffect(() => {
        setLoading(null);
    }, [results]);

    return (
        <>  
            <button onClick={handleClick}>Execute Grid</button>
            {loading ? <h1>{loading}</h1> : results ? (
            <>
                <div className='graphContainer'>
                    <h1>Results over {props.settings.minutes} minutes, or {Math.round(props.settings.minutes/1444*100)/100} days.</h1>
                    <h1>Total Debt is ${Math.round(results['debt']*100)/100}</h1>
                    <h1>Total Assets are: ${Math.round(results['assets']*100)/100}</h1>
                    <h1>Total Profit is ${Math.round(results['profit']*100)/100}</h1>
                    <PandasTable html={results['resultsTable']} />
                </div>
                <div className='graphContainer'>
                    <h1>Final Profit / Debt is {Math.round(results['percent_profit'][results['percent_profit'].length-1]*100)/100}%</h1>
                    <LineChart data={results['percent_profit']} labels={[...Array(results['cv'].length).keys()].map(ele => ele*100)} lineTitle='Profit' text='% Profit vs Time in Minutes' />
                </div>
                <div className='graphContainer'>
                    <LineChart data={results['cv']} labels={[...Array(results['cv'].length).keys()].map(ele => ele*100)} lineTitle='Profit' text='Profit vs Time in Minutes' />
                </div>
                <div className='row'>
                    <div className='imageContainer' >
                        <h1>Smart Grid Graph on {props.tradeSettings.ticker}</h1>
                        <PandasTable html={results['sgHtml']}/>
                    </div>
                    <div className='imageContainer'>
                        <h1>Selling Grid Graph on {props.borrowSettings.ticker}</h1>
                        <PandasTable html={results['selling_grid']}/>
                    </div>
                </div>
                <p>NOTE: The USD gained from the sales in the selling grid is used to purchase the currency in the smart grid, which is then continuously bought and sold.</p>
                <br/>
                {results['data']}
            </>
            ) : null}
        </>
    )
}