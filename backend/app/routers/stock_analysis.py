from fastapi import APIRouter, HTTPException
from ..services import stock_service
from ..models import AnalysisRequest
import re

router = APIRouter()

def detect_market(code: str) -> str:
    # 숫자만 포함된 6자리면 한국 주식
    if re.match(r'^\d{6}$', code):
        return 'KR'
    # 4글자 이하면 미국 주식
    if len(code) <= 4:
        return 'US'
    # 그 외의 경우 입력값에 숫자가 있으면 한국, 없으면 미국
    return 'KR' if any(c.isdigit() for c in code) else 'US'

@router.post("/analyze")
async def analyze_stock(request: AnalysisRequest):
    try:
        # 클라이언트에서 받은 market 값 대신 자동 감지한 값 사용
        market = detect_market(request.ticker)
        result = await stock_service.analyze_stock(request.ticker, market)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators/{ticker}")
async def get_technical_indicators(ticker: str, market: str):
    try:
        # 자동으로 시장 감지
        detected_market = detect_market(ticker)
        indicators = await stock_service.get_technical_indicators(ticker, detected_market)
        return indicators
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))