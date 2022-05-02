
export function PandasTable(props) {
    
    return props.html ? <div className={props.className ? props.className : null} dangerouslySetInnerHTML={{__html: props.html }}></div> : null
}