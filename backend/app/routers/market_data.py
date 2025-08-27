from fastapi import APIRouter, HTTPException
from ..services import market_service

router = APIRouter()

@router.get("/search")
async def search_stocks(query: str, market: str):
    try:
        results = await market_service.search_stocks(query, market)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-status")
async def get_market_status(market: str):
    try:
        status = await market_service.get_market_status(market)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))