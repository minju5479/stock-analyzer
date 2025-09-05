import yfinance as yf
from pykrx import stock
import pandas as pd
import numpy as np
from typing import List
from ..models import StockAnalysis, TechnicalIndicators, ChartData
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def analyze_stock(ticker: str, market: str, timeframe: str = 'daily') -> StockAnalysis:
    try:
        # 시장에 따라 적절한 데이터 소스 선택
        if market.lower() == "kr":
            data = await _get_korean_stock_data(ticker, timeframe)
        else:
            data = await _get_us_stock_data(ticker, timeframe)
        
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")

        # 기술적 분석 수행
        close_prices = data['Close'].values if 'Close' in data.columns else data['종가'].values
        volume = data['Volume'].values if 'Volume' in data.columns else data['거래량'].values
        
        current_price = close_prices[-1]
        prev_price = close_prices[-2]
        change_percent = ((current_price - prev_price) / prev_price) * 100

        indicators = await _calculate_technical_indicators(data)
        rsi_values = await _calculate_rsi_series(data)
        
        # 차트 데이터 준비
        dates = data.index.strftime('%Y-%m-%d').tolist()
        prices = [float(x) for x in close_prices]
        volumes = [int(x) for x in volume]
        
        chart_data = ChartData(
            dates=dates,
            prices=prices,
            volumes=volumes,
            rsi=rsi_values,
            timeframe=timeframe
        )
        
        analysis = StockAnalysis(
            ticker=ticker,
            market=market,
            current_price=float(current_price),
            change_percent=float(change_percent),
            volume=int(volume[-1]),
            indicators=indicators,
            recommendation=_get_recommendation(indicators),
            analysis_summary=_generate_analysis_summary(indicators, change_percent),
            timestamp=datetime.now().isoformat(),
            chart_data=chart_data
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing stock {ticker}: {str(e)}")
        raise

async def _get_korean_stock_data(ticker: str, timeframe: str = 'daily') -> pd.DataFrame:
    try:
        end_date = datetime.now()
        ticker = ticker.zfill(6)
        
        # timeframe에 따라 시작 날짜와 간격 조정
        timeframe_settings = {
            '1m': (1, 'min'),
            '3m': (1, 'min'), 
            '5m': (1, 'min'),
            '10m': (1, 'min'),
            '15m': (1, 'min'),
            '30m': (1, 'min'),
            '60m': (1, 'min'),
            '120m': (1, 'min'),
            '240m': (1, 'min'),
            'daily': (365, 'day'),
            'weekly': (365 * 3, 'week'),  # 더 많은 데이터를 가져와서 주봉 생성
            'monthly': (365 * 5, 'month')  # 더 많은 데이터를 가져와서 월봉 생성
        }
        
        days, interval = timeframe_settings.get(timeframe, (365, 'day'))
        start_date = end_date - timedelta(days=days)
        
        # 분 단위 데이터 요청인 경우
        if interval == 'min':
            # Note: pykrx는 분 단위 데이터를 제공하지 않으므로 다른 데이터 소스 사용 필요
            raise NotImplementedError("Korean stock minute data not yet implemented")

        # 주간/월간 데이터 처리 - pykrx는 간격 파라미터를 지원하지 않으므로 일간 데이터를 가져와서 리샘플링
        if interval in ['week', 'month']:
            # 일간 데이터를 먼저 가져옴
            try:
                logger.info(f"Fetching daily data for resampling to {interval} for ticker {ticker}")
                df = stock.get_market_ohlcv_by_date(
                    start_date.strftime("%Y%m%d"),
                    end_date.strftime("%Y%m%d"),
                    ticker
                )
                
                if df.empty:
                    logger.warning(f"No daily data available for ticker {ticker}")
                    raise ValueError("No daily data available for resampling")
                
                logger.info(f"Successfully fetched {len(df)} daily records, resampling to {interval}")
                
                # 주간/월간으로 리샘플링
                if interval == 'week':
                    df = df.resample('W').agg({
                        '시가': 'first',
                        '고가': 'max', 
                        '저가': 'min',
                        '종가': 'last',
                        '거래량': 'sum'
                    }).dropna()
                elif interval == 'month':
                    df = df.resample('M').agg({
                        '시가': 'first',
                        '고가': 'max',
                        '저가': 'min', 
                        '종가': 'last',
                        '거래량': 'sum'
                    }).dropna()
                
                logger.info(f"Resampled to {len(df)} {interval} records")
                
                if not df.empty:
                    return df
                else:
                    logger.warning(f"Resampled data is empty for {interval}")
                    
            except Exception as e:
                logger.error(f"Failed to fetch and resample {interval} data: {str(e)}", exc_info=True)
        else:  # 일간 데이터 처리
            for i in range(5):
                try_date = end_date - timedelta(days=i)
                try:
                    df = stock.get_market_ohlcv_by_date(
                        start_date.strftime("%Y%m%d"),
                        try_date.strftime("%Y%m%d"),
                        ticker
                    )
                    if not df.empty:
                        return df
                except Exception as e:
                    logger.warning(f"Failed to fetch data for date {try_date.strftime('%Y%m%d')}: {str(e)}")
        
        raise ValueError(f"No data found for Korean stock {ticker}")
    except Exception as e:
        logger.error(f"Error fetching Korean stock data: {str(e)}")
        raise ValueError(f"Failed to fetch data for Korean stock {ticker}")

async def _get_us_stock_data(ticker: str, timeframe: str = 'daily') -> pd.DataFrame:
    try:
        stock_data = yf.Ticker(ticker)
        
        # timeframe에 따라 적절한 기간과 간격 설정
        # yfinance 지원 간격만 사용: 1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo
        period_map = {
            '1m': ("1d", "1m"),      # 1분봉: 최대 1일
            '5m': ("5d", "5m"),      # 5분봉: 최대 5일
            '15m': ("5d", "15m"),    # 15분봉: 최대 5일
            '30m': ("5d", "30m"),    # 30분봉: 최대 5일
            '60m': ("7d", "60m"),    # 60분봉: 최대 7일
            'daily': ("1y", "1d"),   # 일봉
            'weekly': ("2y", "1wk"), # 주봉
            'monthly': ("5y", "1mo"), # 월봉
        }
        
        period, interval = period_map.get(timeframe, ("1y", "1d"))
        
        try:
            logger.info(f"Fetching US stock {ticker} data with period={period}, interval={interval} for timeframe={timeframe}")
            df = stock_data.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for US stock {ticker} with timeframe {timeframe}")
                    
        except Exception as e:
            logger.error(f"Error fetching US stock data for {ticker} with timeframe {timeframe}: {str(e)}")
            raise ValueError(f"Failed to fetch data for US stock {ticker}: {str(e)}")
            
        logger.info(f"Successfully fetched {len(df)} records for US stock {ticker}")
        return df
    except Exception as e:
        logger.error(f"Error fetching US stock data: {str(e)}")
        raise ValueError(f"Failed to fetch data for US stock {ticker}")

async def get_technical_indicators(ticker: str, market: str, timeframe: str = 'daily') -> TechnicalIndicators:
    try:
        if market.lower() == "kr":
            data = await _get_korean_stock_data(ticker, timeframe)
        else:
            data = await _get_us_stock_data(ticker, timeframe)
        
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")

        return await _calculate_technical_indicators(data)
    except Exception as e:
        logger.error(f"Error getting technical indicators for {ticker}: {str(e)}")
        raise

async def _calculate_rsi_series(data: pd.DataFrame, period: int = 14) -> List[float]:
    try:
        close_prices = data['Close'].values if 'Close' in data.columns else data['종가'].values
        delta = pd.Series(close_prices).diff()
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return [float(x) if not pd.isna(x) else 50.0 for x in rsi]
    except Exception as e:
        logger.error(f"Error calculating RSI series: {str(e)}")
        raise

def _clean_float_value(value):
    """Handle NaN and Infinity values for JSON serialization"""
    if pd.isna(value) or np.isinf(value):
        return None
    return float(value)

async def _calculate_technical_indicators(data: pd.DataFrame) -> TechnicalIndicators:
    try:
        close_prices = data['Close'].values if 'Close' in data.columns else data['종가'].values
        
        # Calculate SMA
        sma_50 = pd.Series(close_prices).rolling(window=50).mean().iloc[-1]
        sma_200 = pd.Series(close_prices).rolling(window=200).mean().iloc[-1]

        # Calculate RSI
        delta = pd.Series(close_prices).diff()
        gains = delta.where(delta > 0, 0).rolling(window=14).mean()
        losses = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gains / losses
        rsi = 100 - (100 / (1 + rs.iloc[-1]))

        # Calculate MACD
        exp1 = pd.Series(close_prices).ewm(span=12, adjust=False).mean()
        exp2 = pd.Series(close_prices).ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - signal_line

        # Calculate Bollinger Bands
        middle_band = pd.Series(close_prices).rolling(window=20).mean()
        std_dev = pd.Series(close_prices).rolling(window=20).std()
        upper_band = middle_band + (std_dev * 2)
        lower_band = middle_band - (std_dev * 2)

        return TechnicalIndicators(
            sma_50=_clean_float_value(sma_50),
            sma_200=_clean_float_value(sma_200),
            rsi=_clean_float_value(rsi),
            macd={
                "macd": _clean_float_value(macd_line.iloc[-1]),
                "signal": _clean_float_value(signal_line.iloc[-1]),
                "histogram": _clean_float_value(macd_hist.iloc[-1])
            },
            bollinger_bands={
                "upper": [_clean_float_value(x) for x in upper_band.tail(20).tolist()],
                "middle": [_clean_float_value(x) for x in middle_band.tail(20).tolist()],
                "lower": [_clean_float_value(x) for x in lower_band.tail(20).tolist()]
            }
        )
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        raise

def _get_recommendation(indicators: TechnicalIndicators) -> str:
    try:
        buy_signals = 0
        sell_signals = 0

        # RSI 기반 신호
        if indicators.rsi is not None:
            if indicators.rsi < 30:
                buy_signals += 1
            elif indicators.rsi > 70:
                sell_signals += 1

        # MACD 기반 신호
        if indicators.macd.get('macd') is not None and indicators.macd.get('histogram') is not None:
            if indicators.macd['macd'] > 0 and indicators.macd['histogram'] > 0:
                buy_signals += 1
            elif indicators.macd['macd'] < 0 and indicators.macd['histogram'] < 0:
                sell_signals += 1

        # SMA 기반 신호
        if indicators.sma_50 is not None and indicators.sma_200 is not None:
            if indicators.sma_50 > indicators.sma_200:
                buy_signals += 1
            else:
                sell_signals += 1

        if buy_signals > sell_signals:
            return "매수"
        elif sell_signals > buy_signals:
            return "매도"
        else:
            return "관망"
    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}")
        return "관망"

def _generate_analysis_summary(indicators: TechnicalIndicators, change_percent: float) -> str:
    try:
        summary_parts = []

        # 가격 동향
        if change_percent > 0:
            summary_parts.append(f"최근 상승세를 보이고 있으며, 전일 대비 {abs(change_percent):.2f}% 상승했습니다.")
        else:
            summary_parts.append(f"최근 하락세를 보이고 있으며, 전일 대비 {abs(change_percent):.2f}% 하락했습니다.")

        # RSI 분석
        if indicators.rsi is not None:
            if indicators.rsi < 30:
                summary_parts.append("RSI 지표상 과매도 구간에 있어 반등 가능성이 있습니다.")
            elif indicators.rsi > 70:
                summary_parts.append("RSI 지표상 과매수 구간에 있어 조정 가능성이 있습니다.")
            else:
                summary_parts.append("RSI 지표는 중립적인 범위에 있습니다.")

        # 이동평균선 분석
        if indicators.sma_50 is not None and indicators.sma_200 is not None:
            if indicators.sma_50 > indicators.sma_200:
                summary_parts.append("50일 이동평균선이 200일 이동평균선 위에 위치하여 장기적인 상승 추세를 보이고 있습니다.")
            else:
                summary_parts.append("50일 이동평균선이 200일 이동평균선 아래에 위치하여 장기적인 하락 추세를 보이고 있습니다.")

        return " ".join(summary_parts)
    except Exception as e:
        logger.error(f"Error generating analysis summary: {str(e)}")
        return "기술적 분석 요약을 생성할 수 없습니다."