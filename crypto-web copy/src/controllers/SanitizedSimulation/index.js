import {useState} from "react";
import {SanitizedSim} from "./SanitizedSim";
import {BorrowQuery} from "./BorrowQuery";

export function SanitizedIndex(props) {
    const [borrowQuery, setBorrowQuery] = useState(null);
    const criteria = ["Volume", "Price Performance", "Standard Deviation", "Relative Value", "24h Range"];
    const relativeCriteria = ["Volume/Mean", "Price Performance/Mean", "Standard Deviation/Mean", "Relative Value/Mean", "24h Range/Mean"];
    
    function finished (stuff) {
        setBorrowQuery(stuff);
    }
    return (
        <div>
            {!borrowQuery ? <SanitizedSim length={props.length} tickers={props.tickers} age={props.age} criteria={criteria} relativeCriteria={relativeCriteria} finished={finished} /> : <BorrowQuery data={borrowQuery}/>}
        </div>
    )
}
