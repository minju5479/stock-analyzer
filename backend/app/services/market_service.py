from pykrx import stock as kr_stock
import yfinance as yf
from typing import List, Dict

async def search_stocks(query: str, market: str) -> List[Dict]:
    if market.lower() == "kr":
        return await _search_korean_stocks(query)
    else:
        return await _search_us_stocks(query)

async def get_market_status(market: str) -> Dict:
    if market.lower() == "kr":
        return await _get_korean_market_status()
    else:
        return await _get_us_market_status()

async def _search_korean_stocks(query: str) -> List[Dict]:
    try:
        # pykrx를 사용하여 한국 주식 검색
        market_list = kr_stock.get_market_ticker_list()
        results = []
        for ticker in market_list:
            name = kr_stock.get_market_ticker_name(ticker)
            if query.lower() in name.lower() or query in ticker:
                results.append({
                    "ticker": ticker,
                    "name": name,
                    "market": "KR"
                })
        return results
    except Exception as e:
        return []

async def _search_us_stocks(query: str) -> List[Dict]:
    try:
        # yfinance를 사용하여 미국 주식 검색
        # 실제 구현에서는 더 나은 검색 API를 사용할 수 있습니다
        ticker = yf.Ticker(query)
        info = ticker.info
        return [{
            "ticker": info.get("symbol"),
            "name": info.get("longName"),
            "market": "US"
        }]
    except Exception as e:
        return []

async def _get_korean_market_status() -> Dict:
    try:
        # 한국 시장 상태 확인 로직 구현
        return {"status": "open", "market": "KR"}
    except Exception as e:
        return {"status": "unknown", "market": "KR"}

async def _get_us_market_status() -> Dict:
    try:
        # 미국 시장 상태 확인 로직 구현
        return {"status": "open", "market": "US"}
    except Exception as e:
        return {"status": "unknown", "market": "US"}