import yfinance as yf
from pykrx import stock
import pandas as pd
import numpy as np
from ..models import StockAnalysis, TechnicalIndicators, ChartData
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def analyze_stock(ticker: str, market: str) -> StockAnalysis:
    try:
        # 시장에 따라 적절한 데이터 소스 선택
        if market.lower() == "kr":
            data = await _get_korean_stock_data(ticker)
        else:
            data = await _get_us_stock_data(ticker)
        
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")

        # 기술적 분석 수행
        close_prices = data['Close'].values if 'Close' in data.columns else data['종가'].values
        volume = data['Volume'].values if 'Volume' in data.columns else data['거래량'].values
        
        current_price = close_prices[-1]
        prev_price = close_prices[-2]
        change_percent = ((current_price - prev_price) / prev_price) * 100

        indicators = await _calculate_technical_indicators(data)
        
        # 차트 데이터 준비
        dates = data.index.strftime('%Y-%m-%d').tolist()
        prices = [float(x) for x in close_prices]
        volumes = [int(x) for x in volume]
        
        chart_data = ChartData(
            dates=dates,
            prices=prices,
            volumes=volumes
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

async def get_technical_indicators(ticker: str, market: str) -> TechnicalIndicators:
    try:
        if market.lower() == "kr":
            data = await _get_korean_stock_data(ticker)
        else:
            data = await _get_us_stock_data(ticker)
        
        if data.empty:
            raise ValueError(f"No data found for ticker {ticker}")

        return await _calculate_technical_indicators(data)
    except Exception as e:
        logger.error(f"Error getting technical indicators for {ticker}: {str(e)}")
        raise

async def _get_korean_stock_data(ticker: str) -> pd.DataFrame:
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # 종목 코드가 6자리가 아닌 경우 6자리로 맞추기
        ticker = ticker.zfill(6)
        
        # 최대 5일 전까지 데이터 확인 (주말/공휴일 고려)
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
        
        # 5일 동안 시도했는데도 데이터가 없는 경우
        raise ValueError(f"No data found for Korean stock {ticker} in the last 5 days")
    except Exception as e:
        logger.error(f"Error fetching Korean stock data: {str(e)}")
        raise ValueError(f"Failed to fetch data for Korean stock {ticker}")

async def _get_us_stock_data(ticker: str) -> pd.DataFrame:
    try:
        stock_data = yf.Ticker(ticker)
        df = stock_data.history(period="1y")
        if df.empty:
            raise ValueError(f"No data found for US stock {ticker}")
        return df
    except Exception as e:
        logger.error(f"Error fetching US stock data: {str(e)}")
        raise ValueError(f"Failed to fetch data for US stock {ticker}")

def _get_recommendation(indicators: TechnicalIndicators) -> str:
    try:
        buy_signals = 0
        sell_signals = 0

        # RSI 기반 신호
        if indicators.rsi < 30:
            buy_signals += 1
        elif indicators.rsi > 70:
            sell_signals += 1

        # MACD 기반 신호
        if indicators.macd['macd'] > 0 and indicators.macd['histogram'] > 0:
            buy_signals += 1
        elif indicators.macd['macd'] < 0 and indicators.macd['histogram'] < 0:
            sell_signals += 1

        # SMA 기반 신호
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
        if indicators.rsi < 30:
            summary_parts.append("RSI 지표상 과매도 구간에 있어 반등 가능성이 있습니다.")
        elif indicators.rsi > 70:
            summary_parts.append("RSI 지표상 과매수 구간에 있어 조정 가능성이 있습니다.")
        else:
            summary_parts.append("RSI 지표는 중립적인 범위에 있습니다.")

        # 이동평균선 분석
        if indicators.sma_50 > indicators.sma_200:
            summary_parts.append("50일 이동평균선이 200일 이동평균선 위에 위치하여 장기적인 상승 추세를 보이고 있습니다.")
        else:
            summary_parts.append("50일 이동평균선이 200일 이동평균선 아래에 위치하여 장기적인 하락 추세를 보이고 있습니다.")

        return " ".join(summary_parts)
    except Exception as e:
        logger.error(f"Error generating analysis summary: {str(e)}")
        return "기술적 분석 요약을 생성할 수 없습니다."

async def _calculate_technical_indicators(data: pd.DataFrame) -> TechnicalIndicators:
    try:
        close_prices = data['Close'].values if 'Close' in data.columns else data['종가'].values
        
        # Calculate SMA
        sma_50 = pd.Series(close_prices).rolling(window=50).mean().iloc[-1]
        sma_200 = pd.Series(close_prices).rolling(window=200).mean().iloc[-1]

        # Calculate RSI
        delta = pd.Series(close_prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
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
            sma_50=float(sma_50),
            sma_200=float(sma_200),
            rsi=float(rsi),
            macd={
                "macd": float(macd_line.iloc[-1]),
                "signal": float(signal_line.iloc[-1]),
                "histogram": float(macd_hist.iloc[-1])
            },
            bollinger_bands={
                "upper": [float(x) for x in upper_band.tail(20).tolist()],
                "middle": [float(x) for x in middle_band.tail(20).tolist()],
                "lower": [float(x) for x in lower_band.tail(20).tolist()]
            }
        )
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {str(e)}")
        raise