import {MaForm} from "../controllers/MaForm";
import {useEffect, useState} from 'react';
import { PriceChange } from "../controllers/PriceChangeForm";
import {StartSimulation} from "../controllers/Simulation/StartSimulation";
import {SanitizedIndex} from "../controllers/SanitizedSimulation/index";
import { SmartGrid } from "../controllers/SmartGrid/SmartGridIndex";

export function ButtonComponent(props) {
    const [display, setDisplay] = useState(false);
    const [query, setQuery] = useState('');
    const [elements, setElements] = useState(null);
    const [secondaryQuery, setSecondaryQuery] = useState('');
    const [secondaryElements, setSecondaryElements] = useState('');
    const [simComponent, setSimComponent] = useState('');


    function clickHandler(e) {
        const buttonName = e.target.id;
        setDisplay(true);
        setQuery(buttonName);
    }

    function secondaryClickHandler(e) {
        const buttonName = e.target.id;
        setSecondaryQuery(buttonName);
    }

    useEffect(() => {
        setElements(props.queries.map(elem => {
                return (
                <button disabled={display || elem==="Sanitized Simulation" || elem==="Run Live Smart Grid"} name={elem} id={elem} key={elem} onClick={clickHandler}>{elem}</button>
                )
            })
        )
        setSecondaryElements(props.secondary.map(elem => {
            return (
            <button name={elem} id={elem} key={elem} onClick={secondaryClickHandler}>{elem}</button>
            )
        })
    )
    if (query==="Standard Grid Simulation" && props.tickers) {
        setSimComponent(<div><StartSimulation length={props.length} tickers={props.tickers}/></div>)
    } else if (query==="Sanitized Simulation" && props.tickers) {
        setSimComponent(<div><SanitizedIndex length={props.length} tickers={props.tickers} age={props.age} /></div>)
    } else if (query==="Smart Grid Simulation" && props.tickers) {
        setSimComponent(<div><SmartGrid length={props.length} tickers={props.tickers} age={props.age} /></div>)
    }
    }, [display, props.queries, query, props.secondary, props.length, props.tickers, props.age]);

    function reset() {
        setDisplay(false);
        setSimComponent('');
        setQuery('');
        setSecondaryQuery('');
    }

    const primaryButtons = elements ? (
    <div>
        {elements[0]}
        <br/>
        {elements.slice(1)}
    </div>
    ) : null


    return (
        <div>
            <h1>Margin Grid Trading Simulator</h1>
            <h3>{`Database contains ${props.length} minutes of data.`}</h3>
            <h3>{`Most Recent Data Point is: ${Math.round(props.age*100)/100} minutes old.`}</h3>
            {elements ? primaryButtons: "Loading..."}
            <br/>
            <h1>{display ? query : null}</h1>
            {query === "Query Coin Data" ? secondaryElements : null}
            <h2>{secondaryQuery ? secondaryQuery : null }</h2>
            {display && secondaryQuery === "Moving Average" && props.tickers ? <MaForm tickers={props.tickers} length={props.length}/> : null}
            {display && secondaryQuery === "Price Change" ? <PriceChange length={props.length}/> : null}
            {simComponent}
            <div>
                {display && query ? <button onClick={reset}>Start Over</button> : null}
            </div>
        </div>
    )
}