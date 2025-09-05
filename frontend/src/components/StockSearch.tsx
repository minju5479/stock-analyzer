import React, { useState } from 'react'
import {
  TextField,
  Button,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material'
import { StockAnalysis, TimeFrame } from '../types'
import { AnalysisResult } from './AnalysisResult'

export const StockSearch: React.FC = () => {
  const [ticker, setTicker] = useState('')
  const [analysis, setAnalysis] = useState<StockAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [timeframe, setTimeframe] = useState<TimeFrame>('daily')

  const detectMarket = (code: string): string => {
    // 숫자만 포함된 6자리면 한국 주식
    if (/^\d{6}$/.test(code)) {
      return 'KR'
    }
    // 4글자 이하면 미국 주식
    if (code.length <= 4) {
      return 'US'
    }
    // 그 외의 경우 입력값에 숫자가 있으면 한국, 없으면 미국
    return /\d/.test(code) ? 'KR' : 'US'
  }

  const fetchStockData = async (stockTicker: string, selectedTimeframe: string) => {
    if (!stockTicker) {
      throw new Error('종목 코드를 입력해주세요.')
    }

    const market = detectMarket(stockTicker)
    
    // Korean stocks don't support minute-level data
    if (market === 'KR' && selectedTimeframe.endsWith('m')) {
      throw new Error('한국 주식은 분 단위 데이터를 지원하지 않습니다. 일/주/월 단위를 선택해주세요.')
    }

    const response = await fetch(`http://127.0.0.1:8000/api/analysis/analyze?timeframe=${selectedTimeframe}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ticker: stockTicker,
        market,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || '분석 중 오류가 발생했습니다.')
    }

    return response.json()
  }

  const handleSearch = async (newTimeframe?: TimeFrame) => {
    if (!ticker) {
      setError('종목 코드를 입력해주세요.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const selectedTimeframe = newTimeframe || timeframe
      if (newTimeframe) {
        setTimeframe(newTimeframe)
      }
      
      const data = await fetchStockData(ticker, selectedTimeframe)
      setAnalysis(data)
    } catch (error) {
      setError(error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.')
      setAnalysis(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
          <TextField
            label="종목 코드 (예: 005930 또는 AAPL)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            variant="outlined"
            error={Boolean(error)}
            helperText={error}
            disabled={loading}
            sx={{ minWidth: 200 }}
          />
          <Button
            variant="contained"
            onClick={() => handleSearch()}
            disabled={loading}
            sx={{ height: 56 }}
          >
            {loading ? <CircularProgress size={24} /> : '분석'}
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {analysis && <AnalysisResult analysis={analysis} onTimeframeChange={(newTimeframe: TimeFrame) => {
        setTimeframe(newTimeframe);
        handleSearch(newTimeframe);
      }} />}
    </Box>
  )
}