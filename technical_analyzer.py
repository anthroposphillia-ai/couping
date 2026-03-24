import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_technical_indicators(stock_code):
    """
    이동평균선(20, 60) 및 매물대 돌파 확률을 계산합니다.
    """
    print(f"--- [{stock_code} 기술적 지표 분석] ---")
    
    # 최근 100일 데이터 수집
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=150)).strftime('%Y-%m-%d')
    df = fdr.DataReader(stock_code, start_date)
    
    if df.empty: return None
    
    # 1. 이동평균선 계산
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    
    curr_price = df['Close'].iloc[-1]
    ma20 = df['MA20'].iloc[-1]
    ma60 = df['MA60'].iloc[-1]
    
    # 2. 전고점 매물대 분석 (최근 60일 고가)
    resistance = df['High'].tail(60).max()
    dist_to_res = ((resistance - curr_price) / curr_price) * 100
    
    # 3. 돌파 확률 시뮬레이션 (단순 로직)
    score = 50
    if curr_price > ma20: score += 15 # 상향 정배열 초기
    if curr_price > ma60: score += 10
    if dist_to_res < 3.0: score += 20 # 돌파 임박
    
    analysis = {
        'price': curr_price,
        'ma20': round(ma20, 0),
        'ma60': round(ma60, 0),
        'resistance': resistance,
        'breakout_prob': score,
        'status': "정배열/돌파임박" if score >= 80 else "매물대 저항" if score < 60 else "상승 추세중"
    }
    
    print(f"▶ 현재가: {curr_price:,.0f} | MA20: {ma20:,.0f} | MA60: {ma60:,.0f}")
    print(f"▶ 전고점 저항: {resistance:,.0f} ({dist_to_res:+.2f}%)")
    print(f"▶ 기술적 돌파 확률: {score}% ({analysis['status']})")
    
    return analysis

if __name__ == "__main__":
    analyze_technical_indicators("005930") # 삼성전자 테스트
