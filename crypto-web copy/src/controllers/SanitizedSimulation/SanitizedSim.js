import {useEffect, useState, useCallback} from 'react';

export function SanitizedSim(props) {
    const [count, setCount] = useState(1);
    const [selects, setSelects] = useState(null);
    const [secondSelects, setSecondSelects] = useState(null);
    const [criteriaType, setCriteriaType] = useState('absolute');
    const [borrowObj, setBorrowObj] = useState({minutes: 1000, bottom: 90, top: 100, options: ['Volume'], relativeOptions: [],  subset: 100});

    const createLabels = useCallback(() => {
        function createOptions() {
            return props.criteria.map(ele => {
                return <option key={ele} disabled={borrowObj.options.includes(ele)}>{ele}</option>
            });
        }
        function handleOptions(e) {
            const index = e.target.id;
            setBorrowObj(borrowObj => {
                const items = [...borrowObj.options];
                const newItem = e.target.value;
                items[index] = newItem;
                const newBorrowObj = {...borrowObj, options: items};
                return newBorrowObj;
            })
        }
        const arr = [...Array(count).keys()];
        return arr.map((num, index) => {
            return  (
                <div key={"selectForm" + num.toString()}>
                    <select key={"select" + index.toString() + num} name={`criteria${index}`} id={index} style={{width: 200, height:40, fontSize:15, bold: 700, textAlign: 'center'}} value={borrowObj.options[index]} onChange={handleOptions}>
                        {createOptions()}
                        <option>None</option>
                    </select>
                </div>
                )
        })
    }, [count, props.criteria, borrowObj.options]);

    const relativeLabels = useCallback(() => {
        function handleOptions(e) {
            const index = e.target.id;
            setBorrowObj(borrowObj => {
                const items = [...borrowObj.relativeOptions];
                const newItem = e.target.value;
                items[index] = newItem;
                const newBorrowObj = {...borrowObj, relativeOptions: items};
                return newBorrowObj;
            })
        }

        function createRelativeOptions() {
            return props.relativeCriteria.map(ele => {
                return <option key={ele} disabled={borrowObj.relativeOptions.includes(ele)}>{ele}</option>
            });
        }
        const arr = [...Array(count).keys()];
        return arr.map((num, index) => {
            return  (
                <div key={"selectForm" + num.toString()}>
                    <select key={"select" + index.toString() + num} name={`criteria${index}`} id={index} style={{width: 200, height:40, fontSize:15, bold: 700, textAlign: 'center'}} value={borrowObj.relativeOptions[index]} onChange={handleOptions}>
                        {createRelativeOptions()}
                        <option>None</option>
                    </select>
                </div>
                )
        })
    }, [count, props.relativeCriteria, borrowObj.relativeOptions]);

    const handleChange = ((e) => {
        const newCount = e.target.value;
        setCount(Number(newCount));
        if (criteriaType === 'relative') {
            setBorrowObj(borrowObj => {
                if (newCount > borrowObj.relativeOptions.length) {
                    const relativeOptions = [...borrowObj.relativeOptions];
                    relativeOptions.push(props.relativeCriteria[newCount-1])
                    return {...borrowObj, relativeOptions: relativeOptions}
                }
                else {
                    const relativeOptions = [...borrowObj.relativeOptions];
                    const newRelativeOptions = relativeOptions.slice(0, newCount);
                    return {...borrowObj, relativeOptions: newRelativeOptions}
                }
            });
        }
        else if (criteriaType === 'absolute') {
            setBorrowObj(borrowObj => {
                if (newCount > borrowObj.options.length) {
                    const options = [...borrowObj.options];
                    options.push(props.criteria[newCount-1])
                    return {...borrowObj, options: options}
                }
                else {
                    const options = [...borrowObj.options];
                    const newOptions = options.slice(0, newCount);
                    return {...borrowObj, options: newOptions}
                }
            });
        }
        else if (criteriaType === 'both') {
            setBorrowObj(borrowObj => {
                if (newCount > borrowObj.relativeOptions.length) {
                    const relativeOptions = [...borrowObj.relativeOptions];
                    const options = [...borrowObj.options];
                    options.push(props.criteria[newCount-1]);
                    relativeOptions.push(props.relativeCriteria[newCount-1])
                    return {...borrowObj, relativeOptions: relativeOptions, options: options}
                }
                else {
                    const relativeOptions = [...borrowObj.relativeOptions].slice(0, newCount);
                    const options = [...borrowObj.options].slice(0, newCount);
                    return {...borrowObj, options: options, relativeOptions: relativeOptions}
                }
            });
        }
    })

    function criteriaChange(e) {
        const newCriteria = e.target.value;
        if (newCriteria === 'relative') {
            const newOptions = props.relativeCriteria.slice(0, count);
            setBorrowObj(borrowObj => {
                return {...borrowObj, options: [], relativeOptions: newOptions};
            });
        } 
        else if (newCriteria === 'absolute') {
            const newOptions = props.criteria.slice(0, count);
            setBorrowObj(borrowObj => {
                return {...borrowObj, options: newOptions, relativeOptions: []};
            });
        }
        else if (newCriteria === 'both') {
            const newOptions = props.criteria.slice(0, count);
            const relativeOptions = props.relativeCriteria.slice(0, count);
            setBorrowObj(borrowObj => {
                return {...borrowObj, options: newOptions, relativeOptions: relativeOptions};
            });
        }
        setCriteriaType(newCriteria);
    }

    useEffect(() => {
        setSecondSelects(relativeLabels(count));
        setSelects(createLabels(count));
    }, [count, createLabels, relativeLabels])

    function topChange(e) {
        const newValue = Number(e.target.value);
        setBorrowObj(borrowObj => {
            return {...borrowObj, top: newValue}
        });
        if (newValue - 20 > borrowObj.bottom) {
            setBorrowObj(borrowObj => {
                const newBottom = newValue - 20;
                return {...borrowObj, bottom: newBottom};
            });
        }
    }

    function bottomChange(e) {
        const newValue = Number(e.target.value);
        setBorrowObj(borrowObj => {
            return {...borrowObj, bottom: newValue}
        });
        if (newValue + 20 < borrowObj.top) {
            setBorrowObj(borrowObj => {
                const newTop = newValue + 20;
                return {...borrowObj, top: newTop};
            });
        }
    }

    const relativeSubset = (
        <div key="relativeSubset">
            <label>What subset of data would you like to compare with the {borrowObj.minutes} minute mean for the relative metrics?
            <br/>
            <input type="number" max={borrowObj.minutes/2} min="10" step="10" style={{width: "160px"}} value={borrowObj.subset} onChange={(e) => setBorrowObj(borrowObj => {
                return {...borrowObj, subset: e.target.value}
            })}/> minutes
            </label>
        </div>
    )

    const absoluteMetrics = (
    <div style={{  display: "inline-block", border: "1px solid", padding: "1rem 1rem", verticalAlign: "middle"}} key="absoluteMetrics">
        <h3>Absolute Metrics</h3>
        {selects}
    </div>
    )
    const relativeMetrics = (
        <div style={{  display: "inline-block", border: "1px solid", padding: "1rem 1rem", verticalAlign: "middle"}} key="relativeMetrics">
            <h3>Relative Metrics</h3>
            {secondSelects}
        </div>
        );

    function metricSelection() {
        switch (criteriaType) {
            case 'relative':
                return [relativeSubset, relativeMetrics];
            case 'absolute':
                return absoluteMetrics;
            case 'both':
                return [relativeSubset, relativeMetrics, absoluteMetrics];
            default:
                return null;
        }
    }

    return (
        <div>
            <h2>Borrowing</h2>
            <h3>Trade Coins Based on Their Data Over the Previous Window</h3>
            <p>NOTE: 0-10% is 10% best coins, 90-100% is 10% worst coins.</p>
            <br/>
            <form onSubmit={(e)=> {
                e.preventDefault();
                props.finished(borrowObj);
            }}>
                <label>I will use
                <input type="number" min='100' max="3000" value={borrowObj.minutes} step="100" onChange={(e) => setBorrowObj(borrowObj => {
                    return {...borrowObj, minutes: e.target.value}
                }
                    )}></input>
                minutes of data to select assets to trade over the subsequent {borrowObj.minutes} minute window.</label>
                <br/>
                <label>I want to borrow the
                    <input type="number" min="0" max={borrowObj.top-1} value={borrowObj.bottom} style={{marginLeft: 10}} onChange={bottomChange}></input>
                    to
                    <input type="number" min={borrowObj.bottom+1} max="100" value={borrowObj.top} style={{marginLeft: 10}} onChange={topChange}></input>%
                    coins when sorted by
                    <input type="number" min="1" max="5" value={count} onChange={handleChange}></input>
                    <select onChange={criteriaChange} value={criteriaType} style={{width: 200, height:40, fontSize:15, bold: 700, textAlign: 'center'}}>
                        <option value="absolute">Absolute</option>
                        <option value="relative">Relative</option>
                        <option value="both">Absolute and Relative</option>
                    </select>
                    metrics:
                </label>
                <br/>
                {metricSelection()}
                <br/>
                <br/>
                <input type="submit" value="Submit &amp; Continue"></input>
            </form>
        </div>
    )
}