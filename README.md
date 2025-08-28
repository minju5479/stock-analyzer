# Stock Analyzer

주식 기술적 분석 도구입니다. 한국과 미국 주식 시장의 주가를 분석하고 기술적 지표를 시각화합니다.

## 주요 기능

1. 주가 및 기술적 지표 분석
   - 자동 시장 감지 (한국/미국)
   - 다양한 시간대별 차트 제공
     - 분 단위: 1, 3, 5, 10, 15, 30, 60, 120, 240분
     - 장기: 일/주/월
   - 실시간 기술적 지표 계산
     - RSI (Relative Strength Index)
     - MACD (Moving Average Convergence Divergence)
     - 볼린저 밴드
     - SMA (Simple Moving Average) 50일/200일

2. 차트 시각화
   - 캔들스틱 차트
   - 거래량 차트
   - RSI 차트
   - 반응형 디자인

## 기술 스택

### Frontend
- React
- TypeScript
- Material-UI
- Chart.js

### Backend
- FastAPI
- Python
- yfinance (미국 주식 데이터)
- pykrx (한국 주식 데이터)

## 설치 방법

1. 레포지토리 클론
```bash
git clone https://github.com/minju5479/stock-analyzer.git
cd stock-analyzer
```

2. 백엔드 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. 프론트엔드 설정
```bash
cd frontend
npm install
```

## 실행 방법

1. 백엔드 서버 실행
```bash
cd backend
source venv/bin/activate  # Windows: .\venv\Scripts\activate
uvicorn app.main:app --reload
```

2. 프론트엔드 실행
```bash
cd frontend
npm run dev
```

## API 엔드포인트

### POST /api/analysis/analyze
주식 분석 데이터를 요청합니다.

요청 파라미터:
- `ticker`: 종목 코드 (예: "005930" 또는 "AAPL")
- `timeframe`: 시간 단위 (1m, 3m, 5m, 10m, 15m, 30m, 60m, 120m, 240m, daily, weekly, monthly)

응답:
- 주가 데이터
- 거래량
- 기술적 지표 (RSI, MACD, 볼린저 밴드)
- 투자 추천
- 분석 요약

## 주의사항

1. 한국 주식의 분 단위 데이터는 현재 지원되지 않습니다 (추후 업데이트 예정).
2. 실시간 데이터의 경우 각 데이터 제공자의 업데이트 주기에 따라 지연될 수 있습니다.

## 라이센스

MIT License

주식 차트 분석 웹 애플리케이션입니다. 한국과 미국 주식 시장의 기술적 분석을 제공합니다.

## 기능

- 한국/미국 주식 검색
- 실시간 시장 상태 확인
- 기술적 분석 (이동평균선, RSI, MACD 등)
- 차트 시각화
- 분석 리포트 생성

## 기술 스택

### Backend
- FastAPI
- pandas
- yfinance (미국 주식 데이터)
- pykrx (한국 주식 데이터)
- pandas-ta (기술적 분석)

### Frontend
- React
- TypeScript
- Material-UI
- Recharts (차트 시각화)

## 설치 및 실행

### Backend

1. Python 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

3. 서버 실행
```bash
uvicorn app.main:app --reload
```

### Frontend

1. 의존성 설치
```bash
cd frontend
npm install
```

2. 개발 서버 실행
```bash
npm run dev
```

## API 문서

서버 실행 후 `http://localhost:8000/docs`에서 Swagger API 문서를 확인할 수 있습니다.