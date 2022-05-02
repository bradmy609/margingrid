import { useEffect, useState } from "react";
import { getData } from "../../../../helpers/postFunction";
import { apiPath } from "../../../../apiPath";

export function MaBTCGrid (props) {
    const [data, setData] = useState(null);
    const [assets, setAssets] = useState(null);

    useEffect(() => {
        async function fetchData () {
            const url = `${apiPath}/api/grid/ma/BTC/${props.minutes}/${props.investment}`;
            const response = await getData(url, props.data)
            if (response) {
                setData(response);
            } else {
                console.log("MA BTC Grid response does not exist.")
            }
        }
        fetchData();
    }, [props.data, props.investment, props.minutes]);

    useEffect(() => {
        if (data) {
            const staticRes = Object.values(data).map(ele => {
                if (typeof ele !== 'string') {
                    return ele['results'];
                } else {
                    return 0;
                }
            });
            const staticArrayTotal = staticRes.reduce((a, b) => a + b, 0);
            setAssets(staticArrayTotal);
        }
    }, [data, props.debt, props.start_investment]);

    return (
        <div className='resultsDiv'>
            <h1>MA BTC Grid Results</h1>
            <h2>Standard Deviations: {props.data[0].std}</h2>
            {data ? (
                <div>
                    <h3>Start Value: ${props.start_investment}</h3>
                    <h3>Total Assets: ${Math.round(assets*100)/100}</h3>
                    <h3>Total Debt: ${props.debt}</h3>
                    <h3>Total Value: ${Math.round((assets-props.debt)*100)/100}</h3>
                    <h2>Profit: ${Math.round((assets-props.debt-props.start_investment)*100)/100}</h2>
                </div>
            ): 'Loading...'}
            {data ? <div dangerouslySetInnerHTML={{__html: data['html']}}></div> : null}
        </div>
    )
}