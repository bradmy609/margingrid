import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export function TestChart(props) {
  const prices = Object.values(props.data[0]);
  const labels = Object.keys(props.data[0]);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Moving Average Graph of ${props.ticker}`,
      },
    },
  };


  const data = {
    labels,
    datasets: [
      {
        label: props.ticker,
        data: labels.map((ele, index) => {return prices[index]}),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
    ],
  };
  return (
  <div>
    <Line options={options} data={data} />
  </div>);
}