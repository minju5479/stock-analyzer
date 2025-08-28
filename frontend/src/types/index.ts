export type TimeFrame = 
  | '1m' | '3m' | '5m' | '10m' | '15m' | '30m'
  | '60m' | '120m' | '240m'
  | 'daily'
  | 'weekly'
  | 'monthly';

export interface ChartData {
  dates: string[];
  prices: number[];
  volumes: number[];
  rsi: number[];
  timeframe: TimeFrame;
}

export interface StockAnalysis {
  ticker: string;
  market: string;
  current_price: number;
  change_percent: number;
  volume: number;
  indicators: {
    sma_50: number;
    sma_200: number;
    rsi: number;
    macd: {
      macd: number;
      signal: number;
      histogram: number;
    };
    bollinger_bands: {
      upper: number[];
      middle: number[];
      lower: number[];
    };
  };
  recommendation: string;
  analysis_summary: string;
  timestamp: string;
  chart_data: ChartData;
}