import React from 'react';
import { Paper, Typography, Grid, Box } from '@mui/material';
import { StockAnalysis } from '../types';
import { StockChart } from './StockChart';

interface AnalysisResultProps {
  analysis: StockAnalysis | null;
  onTimeframeChange?: (timeframe: 'daily' | 'weekly' | 'hourly') => void;
}

export const AnalysisResult: React.FC<AnalysisResultProps> = ({ analysis, onTimeframeChange }) => {
  if (!analysis) return null;

  return (
    <Box>
      {analysis.chart_data && <StockChart chartData={analysis.chart_data} onTimeframeChange={onTimeframeChange || (() => {})} market={analysis.market} />}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              {analysis.ticker} ({analysis.market})
            </Typography>
          </Grid>
          
          {/* 기본 정보 */}
          <Grid item xs={12} md={4}>
            <Box>
              <Typography variant="subtitle1">현재가</Typography>
              <Typography variant="h6">
                {analysis.market === 'KR' 
                  ? `₩${analysis.current_price.toLocaleString()}`
                  : `$${analysis.current_price.toLocaleString()}`}
              </Typography>
            </Box>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1">등락률</Typography>
              <Typography
                variant="h6"
                color={analysis.change_percent >= 0 ? 'success.main' : 'error.main'}
              >
                {analysis.change_percent >= 0 ? '+' : ''}
                {analysis.change_percent.toFixed(2)}%
              </Typography>
            </Box>
          </Grid>

          {/* 기술적 지표 */}
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1">기술적 지표</Typography>
            <Box sx={{ mt: 1 }}>
              <Typography>SMA 50: {analysis.indicators.sma_50.toFixed(2)}</Typography>
              <Typography>SMA 200: {analysis.indicators.sma_200.toFixed(2)}</Typography>
              <Typography>RSI: {analysis.indicators.rsi.toFixed(2)}</Typography>
              <Typography>
                MACD: {analysis.indicators.macd.macd.toFixed(2)}
              </Typography>
            </Box>
          </Grid>

          {/* 분석 결과 */}
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1">투자 제안</Typography>
            <Typography
              variant="h6"
              color={
                analysis.recommendation === '매수'
                  ? 'success.main'
                  : analysis.recommendation === '매도'
                  ? 'error.main'
                  : 'warning.main'
              }
            >
              {analysis.recommendation}
            </Typography>
          </Grid>

          {/* 분석 요약 */}
          <Grid item xs={12}>
            <Typography variant="subtitle1">분석 요약</Typography>
            <Typography variant="body1" sx={{ mt: 1, whiteSpace: 'pre-line' }}>
              {analysis.analysis_summary}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};