import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime
import requests
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BOT_TOKEN = "8601832728:AAEZk8B2V1LkyLJAtcTDIwbhZMxS9Wa7GMI"
CHAT_ID = "8627162144"

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def winner_takes_all_analysis(stock_list):
    """
    개장 직후 3분 내 거래대금 회전율이 가장 높은 단 하나의 대장주를 선정합니다.
    """
    print("--- [9:03 Winner-Takes-All 주도주 압축 분석] ---")
    today = datetime.now().strftime('%Y%m%d')
    results = []

    for name, code in stock_list.items():
        try:
            df = fdr.DataReader(code, today)
            if df.empty: continue
            
            # 1. 거래량 파워 분석 (실시간 거래량 / 전일 전체 거래량)
            # 3분 만에 전일 거래량의 상당 부분을 채우면 초강력 수급
            current_vol = df['Volume'].iloc[-1]
            
            # 전일 데이터 가져오기
            df_hist = fdr.DataReader(code, (datetime.now() - pd.Timedelta(days=5)).strftime('%Y%m%d'))
            prev_vol = df_hist['Volume'].iloc[-2]
            
            # 거래량 회전율 (Volume Power)
            vol_power = (current_vol / prev_vol) * 100 if prev_vol > 0 else 0
            
            results.append({
                'name': name,
                'vol_power': vol_power,
                'current_vol': current_vol
            })
        except:
            continue

    # 1순위 종목 선정
    results = sorted(results, key=lambda x: x['vol_power'], reverse=True)
    
    if results:
        winner = results[0]
        msg = f"🏆 [9:03 단일 대장주 압축 포착] \n\n"
        msg += f"오늘의 최우선 공략주는 **{winner['name']}**입니다.\n"
        msg += f"▶ 거래량 폭발력: **{winner['vol_power']:,.2f}%** (개장 3분 만에 전일비)\n"
        msg += f"▶ 현재 체결량: {winner['current_vol']:,.0f}주\n\n"
        msg += f"👉 **Winner-Takes-All**: 오늘 이 종목에 화력을 집중하세요! (강력 매수 신호)"
        send_telegram_msg(msg)
        print(f"대장주 선정 완료: {winner['name']}")

if __name__ == "__main__":
    # 섹터 대장주 후보군
    candidates = {
        '삼성전자': '005930',
        'SK하이닉스': '000660',
        '한미반도체': '042700',
        '가온칩스': '399720',
        '에코프로': '086520'
    }
    winner_takes_all_analysis(candidates)
