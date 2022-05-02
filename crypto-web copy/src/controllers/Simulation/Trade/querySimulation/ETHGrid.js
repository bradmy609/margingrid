import { useState, useEffect } from "react";
import { getData } from "../../../../helpers/postFunction";
import { apiPath } from "../../../../apiPath";

export function ETHGrid (props) {
    const [data, setData] = useState(null);

    useEffect(() => {
        async function getETHGridResults() {
            const url = `${apiPath}/api/static/ETH/${props.minutes}/${props.investment}`;
            const response = await getData(url, props.data)
            if (response) {
                setData(response);
            } else {
                console.log("Static Grid response does not exist.")
            }
        }
        getETHGridResults();
    }, [props.data, props.investment, props.minutes]);

    const staticAssets = () => {
        const staticRes = Object.values(data).map(ele => {
            if (typeof ele !== 'string') {
                return ele['static_grid'];
            } else {
                return 0;
            }
        });
        const staticArrayTotal = staticRes.reduce((a, b) => a + b, 0);
        return staticArrayTotal;
    }

    return (
        <div className='resultsDiv'>
            <h1>Static ETH Grid Results</h1>
            {data ? (
                <div>
                    <h3>Start Value: ${props.start_investment}</h3>
                    <h3>Total Assets: ${Math.round(staticAssets()*100)/100}</h3>
                    <h3>Total Debt: ${props.debt}</h3>
                    <h3>Total Value: ${Math.round((staticAssets()-props.debt)*100)/100}</h3>
                    <h2>Profit: ${Math.round((staticAssets()-props.debt-props.start_investment)*100)/100}</h2>
                </div>
            ): 'Loading...'}
            {data ? <div dangerouslySetInnerHTML={{__html: data['html']}}></div> : null}
        </div>
    )
}