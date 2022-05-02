import {useState} from "react";

export function BorrowQuery(props) {
    return (
        <div>
            {props.data ? JSON.stringify(props.data) : 'poop'}
        </div>
    )
}