import json
import pandas as pd
from datetime import datetime
import FinanceDataReader as fdr
import os

LOG_FILE = "trading_journal.json"

def save_morning_prediction(prediction_data):
    """아침에 생성된 분석 결과를 저장합니다."""
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            
    prediction_data['date'] = datetime.now().strftime('%Y-%m-%d')
    prediction_data['status'] = 'pending'
    logs.append(prediction_data)
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)
    print(f"아침 분석 데이터 저장 완료: {LOG_FILE}")

def update_daily_performance():
    """장 마감 후 성과를 기록하고 피드백을 생성합니다."""
    if not os.path.exists(LOG_FILE): return
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        logs = json.load(f)
        
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    for entry in logs:
        if entry['date'] == today_str and entry['status'] == 'pending':
            # 종목 성과 확인 (삼성전자 예시)
            try:
                df = fdr.DataReader("005930", today_str) # 실제로는 추천 종목 리스트 확인
                if not df.empty:
                    open_price = df['Open'].iloc[0]
                    close_price = df['Close'].iloc[0]
                    change = ((close_price - open_price) / open_price) * 100
                    
                    entry['result_change'] = round(change, 2)
                    entry['success'] = True if change > 0 else False
                    entry['status'] = 'completed'
            except:
                continue
                
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)
    
    print("오늘의 매매 일지 자동 업데이트 완료.")

if __name__ == "__main__":
    # 테스트용
    update_daily_performance()
