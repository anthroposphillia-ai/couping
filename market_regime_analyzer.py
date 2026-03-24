import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_market_regime(index_symbol="KS11"): # KS11: 코스피, KQ11: 코스닥
    """
    최근 5일간의 시장 성격(음봉 연속성)을 분석하여 비중 조절 신호를 생성합니다.
    """
    print(f"--- [{index_symbol} 시장 성격(Regime) 분석] ---")
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
    df = fdr.DataReader(index_symbol, start_date)
    
    if df.empty: return None
    
    # 1. 캔슬 성격 분석 (Open vs Close)
    # 음봉: Open > Close, 양봉: Open < Close
    df['Is_Blue'] = df['Open'] > df['Close']
    
    recent_5d = df.tail(5).copy()
    blue_count = recent_5d['Is_Blue'].sum()
    
    # 연속 음봉 확인 (최근 3일 기준)
    consecutive_blue = 0
    for i in range(1, 4):
        if df['Is_Blue'].iloc[-i]:
            consecutive_blue += 1
        else:
            break
            
    # 2. 비중 조절 로직
    defense_mode = False
    exposure_ratio = 100
    
    if consecutive_blue >= 3:
        defense_mode = True
        exposure_ratio = 50 # 비중 50% 축소
        status_msg = "🚨 경고: 3일 연속 음봉 발생 (방어 모드 활성화)"
    elif blue_count >= 4:
        defense_mode = True
        exposure_ratio = 70 
        status_msg = "⚠️ 주의: 최근 5일 중 4일 음봉 (비중 축소)"
    else:
        status_msg = "✅ 시장 기세 양호 (적정 비중 유지)"
        
    print(f"▶ 최근 5일 중 음봉 횟수: {blue_count}회")
    print(f"▶ 현재 연속 음봉 횟수: {consecutive_blue}회")
    print(f"▶ 결론: {status_msg} (추천 비중: {exposure_ratio}%)")
    
    return {
        'defense_mode': defense_mode,
        'exposure_ratio': exposure_ratio,
        'status_msg': status_msg,
        'consecutive_blue': consecutive_blue
    }

if __name__ == "__main__":
    analyze_market_regime("KS11")
