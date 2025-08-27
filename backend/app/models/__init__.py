from pydantic import BaseModel
from typing import List, Dict, Optional

class AnalysisRequest(BaseModel):
    ticker: str
    market: str

class TechnicalIndicators(BaseModel):
    sma_50: float
    sma_200: float
    rsi: float
    macd: Dict[str, float]
    bollinger_bands: Dict[str, List[float]]

class ChartData(BaseModel):
    dates: List[str]
    prices: List[float]
    volumes: List[int]
    rsi: List[float]
    timeframe: str

class StockAnalysis(BaseModel):
    ticker: str
    market: str
    current_price: float
    change_percent: float
    volume: int
    indicators: TechnicalIndicators
    recommendation: str
    analysis_summary: str
    timestamp: str
    chart_data: ChartData

class MarketStatus(BaseModel):
    market: str
    status: str
    timestamp: str

class StockSearchResult(BaseModel):
    ticker: str
    name: str
    market: str