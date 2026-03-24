import json
import os
import FinanceDataReader as fdr
from datetime import datetime
import requests
import os
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LOG_FILE = "trading_journal.json"
BOT_TOKEN = "8601832728:AAEZk8B2V1LkyLJAtcTDIwbhZMxS9Wa7GMI"
CHAT_ID = "8627162144"

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def generate_daily_feedback():
    if not os.path.exists(LOG_FILE): 
        print("로그 파일이 없습니다.")
        return
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_entry = next((e for e in logs if e['date'] == today_str), None)
    
    if not today_entry:
        print("오늘의 예측 데이터가 없습니다.")
        return

    # 삼성전자 기준으로 오늘의 실제 성과 분석 (테스트용 대용 지표)
    try:
        df = fdr.DataReader("005930", today_str)
        if not df.empty:
            open_p = df['Open'].iloc[0]
            close_p = df['Close'].iloc[0]
            actual_chg = ((close_p - open_p) / open_p) * 100
            
            feedback_msg = f"📊 [장 마감 성과 피드백 리포트] \n\n"
            feedback_msg += f"▶ 아침 진입 점수: {today_entry['score']}점\n"
            feedback_msg += f"▶ 아침 추천 액션: {today_entry['action']}\n"
            feedback_msg += f"▶ 실제 장중 변동(시가대비): {actual_chg:+.2f}%\n\n"
            
            # 자가 수정 (Self-Correction) 로직
            if today_entry['action'] == "AVOID_GAP" and actual_chg < -1.0:
                feedback_msg += "✅ **예측 성공**: 갭 상승 리스크 회피 로직이 정확했습니다.\n"
            elif today_entry['action'] == "ENTRY_OK" and actual_chg > 0.5:
                feedback_msg += "✅ **예측 성공**: 적극 공략 장세 판단이 유효했습니다.\n"
            else:
                feedback_msg += "⚠️ **로직 보정 필요**: 시장 흐름이 예측과 다르게 흘렀습니다.\n"
                feedback_msg += "환율/선물 가중치를 재점검할 필요가 있습니다.\n"

            print(feedback_msg)
            send_telegram_msg(feedback_msg)
            
            # 완료 상태 업데이트
            today_entry['status'] = 'completed'
            today_entry['actual_change'] = round(actual_chg, 2)
            
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Feedback error: {e}")

if __name__ == "__main__":
    generate_daily_feedback()
