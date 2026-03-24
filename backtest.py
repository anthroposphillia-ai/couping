import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import io

# 윈도우 환경에서 한글 출력 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_backtest():
    print("--- [나스닥 반도체(SOXX) vs 삼성전자 백테스팅: 최근 1년] ---")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # 1. 데이터 수집
    print("데이터 수집 중...")
    # SOXX (나스닥 반도체 ETF)
    soxx = yf.download("SOXX", start=start_date, end=end_date)
    # 삼성전자 (005930)
    samsung = fdr.DataReader("005930", start=start_date, end=end_date)
    
    # 2. 데이터 전처리 (날짜 맞추기)
    combined = pd.DataFrame()
    combined['SOXX_Change'] = soxx['Close'].pct_change() * 100
    combined['Samsung_Open_Chg'] = ((samsung['Open'] - samsung['Close'].shift(1)) / samsung['Close'].shift(1)) * 100
    combined['Samsung_OC_Chg'] = ((samsung['Close'] - samsung['Open']) / samsung['Open']) * 100
    combined['Samsung_Close_Chg'] = samsung['Close'].pct_change() * 100
    
    # 전날 미국장 결과가 오늘 국장에 영향을 미침
    combined['SOXX_Prev_Day_Change'] = combined['SOXX_Change'].shift(1)
    combined = combined.dropna()
    
    # 3. 조건 분석
    # 조건 A: 전날 SOXX 2% 이상 상승
    target_days = combined[combined['SOXX_Prev_Day_Change'] >= 2.0]
    total_target_days = len(target_days)
    
    if total_target_days == 0:
        print("최근 1년 동안 SOXX가 2% 이상 상승한 날이 없습니다.")
        return
        
    # 결과 A: 삼성전자가 플러스 마감한 날 (전일 종가 대비)
    win_days = target_days[target_days['Samsung_Close_Chg'] > 0]
    win_count = len(win_days)
    
    # 결과 B: 시초가 대비 양봉 마감 확률 (Open < Close)
    red_candle_days = target_days[target_days['Samsung_OC_Chg'] > 0]
    blue_candle_days = target_days[target_days['Samsung_OC_Chg'] < 0]
    
    # 추가 조건: 시초가가 갭을 3% 이상 띄웠을 때 음봉 확률 (설거지 분석)
    gap_up_days = target_days[target_days['Samsung_Open_Chg'] >= 3.0]
    gap_up_blue_count = len(gap_up_days[gap_up_days['Samsung_OC_Chg'] < 0])
    gap_up_prob = (gap_up_blue_count / len(gap_up_days) * 100) if len(gap_up_days) > 0 else 0

    # 4. 결과 출력
    print(f"\n[기본 통계: SOXX 2%↑ 시]")
    print(f"-> 전체 분석 일수: {total_target_days}일")
    print(f"-> 전일 종가 대비 상승 마감: {win_count}회 ({win_count/total_target_days*100:.2f}%)")
    print(f"-> 시초가 대비 양봉 마감(Open < Close): {len(red_candle_days)}회")
    print(f"-> 시초가 대비 음봉 마감(Open > Close): {len(blue_candle_days)}회")
    
    print(f"\n[설거지(시가고가) 주의보 통계]")
    print(f"-> 갭 3% 이상 상승 출발 횟수: {len(gap_up_days)}회")
    if len(gap_up_days) > 0:
        print(f"-> **갭 3%↑ 출발 시 음봉 마감 확률: {gap_up_prob:.2f}%**")
        print("   (주의: 갭이 높을수록 시초가가 고점이 될 확률이 높음)")

if __name__ == "__main__":
    run_backtest()
