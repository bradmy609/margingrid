import {useCallback, useEffect, useState} from "react";
import { getData } from "../../../../helpers/postFunction";
import { apiPath } from "../../../../apiPath";

export function Query(props) {
    const [data, setData] = useState("Loading...");
    const [display, setDisplay] = useState(true);


    function addClassNames() {
        const listHtml = data['html'].split(' ');
        const indexes = [];
        const thIndexes = [];
        listHtml.forEach((ele, index) => {
            if (ele.includes('<tr>')) {
                indexes.push(index);
            } else if (ele.includes('<th>')) {
                thIndexes.push(index)
            }
        });

        const newList = listHtml.map((ele, index) => {
            if (index === indexes[indexes.length-1] || index === indexes[indexes.length-2]) {
                return "<tr class=tableFooter>";
            } else if (index === thIndexes[thIndexes.length-1]) {
                return "<th class=tableFooter>Total</th>";
            } else if (index === thIndexes[thIndexes.length-2]) {
                return "<th class=tableFooter>Average</th>"
            } else {
                return ele;
            }
        })
        
        const newHtml = newList.join(' ');
        setData(data => {
            const newObj = Object.assign({}, data);
            newObj['html'] = newHtml;
            return newObj;
        })
    }

    const postReq = useCallback(async () => {
            const url = `${apiPath}/api/borrow/${props.minutes}/${Number(props.investment) * Number(props.leverage)}`;
            const response = await getData(url, props.data);
            if (response) {
                setData(response);
            } else {
                console.log("Error, response does not exist!")
            }
        }, [props.data, props.leverage, props.investment, props.minutes]);


    useEffect(() => {
        postReq();
    }, [postReq]);

    function sendUpstream() {
        props.upStream(props.data)
        props.table(data['html']);
    }


    if (data['html'] && !data['html'].includes('tableFooter')) {
        addClassNames();
    }

    function handleClick(e) {
        setDisplay(false);
        sendUpstream();
    }

    return (
        <div>
            {data && display ? 
            (
            <div>
                <h3>Borrowed Coins Data</h3>
                <br/>
                <br/>
                {data['html'] ? <div dangerouslySetInnerHTML={{__html: data['html']}}></div> : "Loading borrow table, please wait..."}
            </div>
            )
             : null}
            {display ? (
            <input type="submit" value="Save and Continue" onClick={handleClick}/>
            ) : null
            }
        </div>
    )
}