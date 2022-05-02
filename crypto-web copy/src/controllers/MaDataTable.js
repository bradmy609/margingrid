import "./styles.css"

export function DataTable(props) {
    const times = Object.keys(props.data[0]);
    const prices = Object.values(props.data[0]);

    const startTime = new Date(times[0]);
    const period = (new Date(times[1]).getTime() - startTime) / 60000;
    const endTime = new Date(times[times.length-1]);
    const startPastMinutes = Math.round((new Date() - startTime)/60000);
    const endPastMinutes = Math.round((new Date() - endTime)/60000);
    const timeDelta = Number(startPastMinutes - endPastMinutes) + period; 

    function renderTableData() {
        return times.map((time, index) => {
            return (
                <tr key={times[index]}>
                    <td>{index+1}</td>
                    <td>{prices[index]}</td>
                    <td>{(new Date() - new Date(time))/60000}</td>
                    <td>{time}</td>
                </tr>
            )
        })
    }

    return (
        <div>
            <h3>{props.ticker}</h3>
            <h5>{`Data Ranges from: ${startTime} to ${endTime}`}</h5>
            <h5>{`Data Ranges from: ${startPastMinutes} minutes ago to ${endPastMinutes - period} minutes ago (${timeDelta} minutes)`}</h5>
            <table className="datatable">
                <tbody>
                    <tr>
                        <th>
                            Index
                        </th>
                        <th>
                            Price
                        </th>
                        <th>
                            Data Age (Minutes)
                        </th>
                        <th>
                            Date/Time
                        </th>
                    </tr>
                {props.data ? renderTableData() : null}
                </tbody>
            </table>
        </div>
    )

}