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
  BarElement,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Paper, Box } from '@mui/material';
import { ChartData } from '../types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface StockChartProps {
  chartData: ChartData;
}

export const StockChart: React.FC<StockChartProps> = ({ chartData }) => {
  const data = {
    labels: chartData.dates,
    datasets: [
      {
        label: '주가',
        data: chartData.prices,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        yAxisID: 'y',
      },
      {
        label: '거래량',
        data: chartData.volumes,
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        type: 'bar',
        yAxisID: 'y1',
      },
    ],
  };

  const options = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: '주가 및 거래량 차트',
      },
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: '주가',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: '거래량',
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
  };

  return (
    <Paper sx={{ p: 3, mt: 3 }}>
      <Box sx={{ height: 400 }}>
        <Line options={options} data={data} />
      </Box>
    </Paper>
  );
};