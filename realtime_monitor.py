import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
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

def analyze_realtime_volume(stock_list):
    """
    개장 직후 거래량 분출 속도를 분석하여 주도주를 선정합니다.
    """
    print("--- [실시간 주도주 수급 분석 엔진 가동] ---")
    today = datetime.now().strftime('%Y%m%d')
    results = []

    for name, code in stock_list.items():
        try:
            # 1. 오늘 실시간 데이터 (FDR 기준 일일 데이터이나 장중에는 현재까지 거래량)
            df_today = fdr.DataReader(code, today)
            if df_today.empty: continue
            current_vol = df_today['Volume'].iloc[-1]

            # 2. 최근 20일 평균 거래량 수집
            start_date = (datetime.now() - timedelta(days=40)).strftime('%Y%m%d')
            df_hist = fdr.DataReader(code, start_date)
            avg_vol_20d = df_hist['Volume'].tail(20).mean()

            # 3. 거래량 분출 속도 (Relative Volume Speed)
            # 9:05 기준이라면 장전체(380분) 중 5분(1.3%)이 흐른 시점
            # 기대 거래량 대비 현재 거래량 비중 계산
            elapsed_ratio = 5 / 380 # 개장 5분 기준
            expected_vol = avg_vol_20d * elapsed_ratio
            vol_speed = (current_vol / expected_vol) * 100 if expected_vol > 0 else 0

            results.append({
                'name': name,
                'speed': vol_speed,
                'current_vol': current_vol
            })
            print(f"[{name}] 현재속도: {vol_speed:.1f}%")
        except Exception as e:
            print(f"Error analyzing {name}: {e}")

    # 속도순 정렬
    results = sorted(results, key=lambda x: x['speed'], reverse=True)
    
    if results:
        top = results[0]
        msg = f"🔥 [9:05 실시간 주도주 포착 리포트] \n\n"
        msg += f"현재 거래량 분출 강도가장 높은 종목은 **{top['name']}**입니다.\n"
        msg += f"▶ 거래 분출 속도: **{top['speed']:,.0f}%** (평균 대비)\n"
        msg += f"▶ 현재 체결량: {top['current_vol']:,.0f}주\n\n"
        msg += f"👉 **오늘의 섹터 대장주**로 판단됩니다. 눌림목 공략을 고려하세요."
        send_telegram_msg(msg)
        print("텔레그램 주도주 속보 전송 완료.")

if __name__ == "__main__":
    # 섹터별 핵심 종목 리스트 (실제 운영 시 DB 연동)
    watch_stocks = {
        '삼성전자': '005930',
        'SK하이닉스': '000660',
        '한미반도체': '042700',
        '가온칩스': '399720',
        '제주반도체': '080220'
    }
    analyze_realtime_volume(watch_stocks)
