import React, { useState } from 'react';
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
import { Paper, Box, ToggleButton, ToggleButtonGroup } from '@mui/material';
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

import { TimeFrame } from '../types';

interface StockChartProps {
  chartData: ChartData;
  onTimeframeChange: (timeframe: TimeFrame) => void;
  market: string;
}

export const StockChart: React.FC<StockChartProps> = ({ chartData, onTimeframeChange, market }) => {
  const [timeframe, setTimeframe] = useState<TimeFrame>(chartData.timeframe);

  const timeframeGroups = [
    ...(market.toUpperCase() === 'US' ? [{
      label: '분',
      options: [
        { value: '1m', label: '1분' },
        { value: '3m', label: '3분' },
        { value: '5m', label: '5분' },
        { value: '10m', label: '10분' },
        { value: '15m', label: '15분' },
        { value: '30m', label: '30분' },
        { value: '60m', label: '60분' },
        { value: '120m', label: '120분' },
        { value: '240m', label: '240분' },
      ]
    }] : []),
    {
      label: '장기',
      options: [
        { value: 'daily', label: '일' },
        { value: 'weekly', label: '주' },
        { value: 'monthly', label: '월' },
      ]
    }
  ];

  const handleTimeframeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newTimeframe: TimeFrame,
  ) => {
    if (newTimeframe !== null) {
      setTimeframe(newTimeframe);
      onTimeframeChange(newTimeframe);
    }
  };

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
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: '주가 차트',
      },
    },
    scales: {
      x: {
        grid: {
          display: true,
        },
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: '주가',
        },
      },
    },
  };

  const volumeChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: '거래량',
      },
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        position: 'right' as const,
      },
    },
  };

  const rsiChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: 'RSI',
      },
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        display: true,
      },
      y: {
        min: 0,
        max: 100,
        position: 'right' as const,
      },
    },
  };

  const volumeChartData = {
    labels: chartData.dates,
    datasets: [
      {
        label: '거래량',
        data: chartData.volumes,
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        borderColor: 'rgb(53, 162, 235)',
      },
    ],
  };

  const rsiData = {
    labels: chartData.dates,
    datasets: [
      {
        label: 'RSI',
        data: chartData.rsi,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.4,
      },
    ],
  };

  return (
    <Paper sx={{ p: 3, mt: 3 }}>
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {timeframeGroups.map((group) => (
            <ToggleButtonGroup
              key={group.label}
              value={timeframe}
              exclusive
              onChange={handleTimeframeChange}
              aria-label={`${group.label} timeframe`}
              size="small"
            >
              {group.options.map((option) => (
                <ToggleButton
                  key={option.value}
                  value={option.value}
                  aria-label={option.label}
                >
                  {option.label}
                </ToggleButton>
              ))}
            </ToggleButtonGroup>
          ))}
        </Box>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, width: '100%' }}>
        <Box sx={{ height: '400px', width: '100%' }}>
          <Line options={options} data={data} />
        </Box>
        <Box sx={{ height: '200px', width: '100%' }}>
          <Line options={volumeChartOptions} data={volumeChartData} />
        </Box>
        <Box sx={{ height: '200px', width: '100%' }}>
          <Line options={rsiChartOptions} data={rsiData} />
        </Box>
      </Box>
    </Paper>
  );
};