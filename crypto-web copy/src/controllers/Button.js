import {useEffect, useState} from "react";
import {ButtonComponent} from "../components/ButtonComponent";
import { apiPath } from "../apiPath";
import "./styles.css";

export default function Button(props) {
    const [data, setData] = useState('Loading...');
    const [length, setLength] = useState('Loading...');
    const [tickers, setTickers] = useState(null);
    const queries = ["Query Coin Data", "Standard Grid Simulation", "Sanitized Simulation", "Smart Grid Simulation", "Run Live Smart Grid"];
    const secondaryQueries = ["Moving Average", "Price Change"]

    useEffect(() => {
        async function getLength() {
            try{
                const response = await fetch(`${apiPath}/api/tickers`);
                if (response.ok) {
                    const jsonRes = await response.json();
                    setTickers(jsonRes['data']);
                    setLength(jsonRes['length']);
                }
            } catch(e) {
                console.log(e);
            }
        }
        async function getAge() {
            try{
                const response = await fetch(`${apiPath}/api/age`);
                if (response.ok) {
                    const textRes = await response.text();
                    setData(textRes);
                }
            } catch(e) {
                console.log(e);
            }
        }
        getAge();
        getLength();
    }, []);
    
    return (
        <ButtonComponent disabled={!tickers} length={length} age={data} queries={queries} secondary={secondaryQueries} tickers={tickers}></ButtonComponent>
        )
};