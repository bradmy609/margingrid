import { useState, useEffect} from "react";
import { getData } from "../../../../helpers/postFunction";
import { apiPath } from "../../../../apiPath";

export function USDTGrid (props) {
    const [results, setResults] = useState([]);
    // const [baseTicker, setBaseTicker] = useState(null);
    
    useEffect(() => {
        const bases = ['USDT', 'ETH', 'BTC', 'KCS'];
        bases.forEach(async (base, index) => {
            const url = `${apiPath}/api/static/${base}/${props.minutes}/${props.investment}`;
            const response = await getData(url, props.data);
            if (response) {
                setResults((results) => {
                    const items = [...results];
                    const item = response;
                    items[index] = item;
                    return items;
                })
                } else {
                    console.log('Error with static grid API queries.')
                }
            })
        }, [props.data, props.minutes, props.investment])

    const staticAssets = (data) => {
        try {
            const staticRes = Object.values(data).map(ele => {
                if (typeof ele !== 'string') {
                    return ele['static_grid'];
                } else {
                    return 0;
                }
            });
            const staticArrayTotal = staticRes.reduce((a, b) => a + b, 0);
            return staticArrayTotal;
        } catch(error) {
            window.alert(Object.values(data));
            console.log(data);
            console.log(error)
        }
    }

    const buildDivs = () => {
        const bases = ['USDT', 'ETH', 'BTC', 'KCS'];
        return results.map((data, index) => {
            // const baseChange = Math.round(data['base_change']*100)/100
            const baseTicker = bases[index];
            return (
            <div key={index} className="resultsDiv">
                <h1>Static {baseTicker} Grid Results</h1>
                <h3>Start Value: ${props.start_investment}</h3>
                <h3>Total Assets: ${Math.round(staticAssets(data)*100)/100}</h3>
                <h3>Total Debt: ${props.debt}</h3>
                <h3>Total Value: {Math.round((staticAssets(data)-props.debt)*100)/100}</h3>
                <h2>Profit: ${Math.round((staticAssets(data)-props.debt-props.start_investment)*100)/100}</h2>
                {data ? <div dangerouslySetInnerHTML={{__html: data['html']}}></div> : null}
            </div>
            )
        });
    };

    useEffect(() => {
        if (results.length === 4) {
            props.complete(true)
        }
    }, [results, props])
    
    return (
        <div>
            {results.length === 4 ? buildDivs(): "Loading..."}
        </div>
    )
}