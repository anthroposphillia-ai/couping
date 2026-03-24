import FinanceDataReader as fdr
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def train_ml_factor_model():
    """
    최근 6개월 데이터를 학습하여 각 지표(선물, 환율, 나스닥)의 중요도를 산출합니다.
    """
    print("--- [AI 지능 고도화: 팩터 가중치 분석 시작] ---")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=200) # 약 6개월 이상
    
    # 1. 데이터 수집
    print("데이터 수집 중 (NQ=F, KRW=X, QQQ, KOSPI)...")
    # squeeze=True 혹은 iloc[:, 0]를 사용하여 1차원으로 확보
    nq_f = yf.download("NQ=F", start=start_date, end=end_date)['Close'].pct_change().squeeze()
    fx = yf.download("KRW=X", start=start_date, end=end_date)['Close'].pct_change().squeeze()
    qqq = yf.download("QQQ", start=start_date, end=end_date)['Close'].pct_change().squeeze()
    
    # 코스피 데이터 (FDR)
    kospi = fdr.DataReader("KS11", start_date, end_date)
    
    # 타겟 데이터: 코스피 시초가 갭 (오늘 시가 vs 전일 종가)
    target = ((kospi['Open'] - kospi['Close'].shift(1)) / kospi['Close'].shift(1)) * 100
    target = target.squeeze()
    
    # 2. 데이터 프레임 합치기 (날짜 기준)
    # 인덱스가 맞지 않을 수 있으므로 조인을 통해 정렬
    df = pd.DataFrame({
        'Futures': nq_f.shift(1),
        'FX': fx.shift(1),
        'Nasdaq': qqq.shift(1),
        'Target': target
    }).dropna()
    
    # 3. Random Forest 학습
    X = df[['Futures', 'FX', 'Nasdaq']]
    y = df['Target']
    
    if len(df) < 20: 
        print("학습 데이터가 부족합니다.")
        return None

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # 4. 중요도 추출
    importances = model.feature_importances_
    factors = X.columns
    
    result = {factors[i]: round(importances[i] * 100, 2) for i in range(len(factors))}
    
    print("\n[AI 분석 결과: 지표별 중요도]")
    for factor, weight in result.items():
        print(f"▶ {factor}: {weight}%")
        
    top_factor = max(result, key=result.get)
    print(f"\n💡 결론: 최근 시장은 '{top_factor}' 지표에 가장 민감하게 반응하고 있습니다.")
    
    return result

if __name__ == "__main__":
    train_ml_factor_model()
