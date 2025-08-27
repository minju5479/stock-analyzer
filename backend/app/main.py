from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import stock_analysis, market_data

app = FastAPI(title="Stock Analysis API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 개발 서버
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(stock_analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(market_data.router, prefix="/api/market", tags=["market"])

@app.get("/")
async def root():
    return {"message": "Welcome to Stock Analysis API"}