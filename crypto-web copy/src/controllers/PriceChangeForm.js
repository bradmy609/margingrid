import {useState} from "react";
import { apiPath } from "../apiPath";

export function PriceChange(props) {
    const [data, setData] = useState();

    async function onSubmit(e) {
        e.preventDefault();
        const startTime = e.target.startTime.value;
        const stopTime = e.target.stopTime.value;
        const top = e.target.radio.value;
        const quantity = e.target.quantity.value;

        try{
            const response = await fetch(`${apiPath}/api/pricedelta/${startTime}/${stopTime}/${top}/${quantity}`);
            if (response.ok) {
                const textRes = await response.text();
                setData(textRes);
            }
        } catch(e) {
            console.log(e);
        }
    }

    return (
        <div>
            <form name="pricechangeform" onSubmit={onSubmit}>
                <label>Start Time (# Minutes From Last Datapoint):
                    <input name="startTime" type="number" defaultValue={props.length-1} />
                </label>
                <br/>
                <label>Stop Time (# Minutes From Last Datapoint 0=Most Recent):
                    <input name="stopTime" type="number" defaultValue="0" />
                </label>
                <br/>
                <label>
                    <input type="radio" id="radiotop" name="radio" value="true"
         defaultChecked/>Best
                </label>
                <label>
                    <input type="radio" id="radiobottom" name="radio" value="false"/>
                    Worst
                </label>
                <br/>
                <label>Quantity:
                    <input name="quantity" type="number" defaultValue="10" />
                </label>
                <br/>
                    <input name="submit" type="submit"/>
                    <input name="reset" type="reset" onClick={() => setData(null)} />
            </form>
            {data ? <div dangerouslySetInnerHTML={{__html: data}}></div> : null}
        </div>
    )
}