# Stock Analyzer

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