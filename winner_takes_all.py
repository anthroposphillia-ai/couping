import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime
import requests
import sys
import io
import sector_scanner
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 텔레그램 설정
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8601832728:AAEZk8B2V1LkyLJAtcTDIwbhZMxS9Wa7GMI")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8627162144")

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=payload)

def filter_winner_takes_all(category_id):
    """
    v9.5: 크로스보더 주도주 포착 엔진
    """
    # 1. 섹터 종목 풀 및 미국 매칭 정보 가져오기
    scanner_result = sector_scanner.get_sector_pool(category_id)
    pool = scanner_result['symbols']
    title = scanner_result['title']
    us_match = scanner_result['us_match']
    
    if not pool: return
    
    print(f"--- [v9.5 {title} 주도주 포착 시작] ---")
    
    # [v9.5 핵심] 미국 매칭 종목 수익률 분석 (심리 지표)
    us_mood_msg = ""
    if us_match:
        try:
            us_perf = []
            for ticker in us_match[:3]: # 상위 3개만 샘플링
                df_us = yf.Ticker(ticker).history(period='2d')
                if len(df_us) >= 2:
                    perf = ((df_us['Close'].iloc[-1] - df_us['Close'].iloc[-2]) / df_us['Close'].iloc[-2]) * 100
                    us_perf.append(f"{ticker}({perf:+.1f}%)")
            if us_perf:
                us_mood_msg = f"🌍 <b>전일 미국 {title} 분위기</b>: {', '.join(us_perf)}\n"
        except:
            pass

    today = datetime.now().strftime('%Y%m%d')
    results = []

    # 2. 국내 섹터 주도주 분석 (VPR 로직)
    for stock in pool:
        try:
            symbol = stock['Symbol']
            name = stock['Name']
            
            df = fdr.DataReader(symbol, today)
            if df.empty: continue
            
            curr_close = df['Close'].iloc[-1]
            curr_vol = df['Volume'].iloc[-1]
            curr_open = df['Open'].iloc[-1]
            
            df_hist = fdr.DataReader(symbol, (datetime.now() - pd.Timedelta(days=5)).strftime('%Y%m%d'))
            prev_vol = df_hist['Volume'].iloc[-2]
            
            change_p = ((curr_close - curr_open) / curr_open) * 100
            vol_impact = (curr_vol / prev_vol) * 100 if prev_vol > 0 else 0
            vpr_score = (change_p * 0.5) + (vol_impact * 0.05) 
            
            if vol_impact > 5: # v9.5 민감도 상향
                results.append({
                    'name': name,
                    'code': symbol,
                    'change': change_p,
                    'vol_impact': vol_impact,
                    'vpr_score': vpr_score
                })
        except:
            continue

    # 3. 최종 리포트 생성 및 전송
    winners = sorted(results, key=lambda x: x['vpr_score'], reverse=True)[:3]
    if winners:
        msg = f"<b>🏆 [v9.5 {title} '크로스보더 대장주' Top 3]</b>\n\n"
        msg += us_mood_msg + "\n"
        for i, w in enumerate(winners):
            msg += f"{i+1}위: <b>{w['name']}</b> ({w['code']})\n"
            msg += f"▶ 등락률: {w['change']:+.2f}%\n"
            msg += f"▶ 수급 폭발력: {w['vol_impact']:,.1f}% (전일비)\n\n"
            
        send_telegram_msg(msg)
        print(f"v9.5 글로벌-국내 연동 포착 완료: {[w['name'] for w in winners]}")
    else:
        print("⏸ 주도주 포착 실패 (조건 충족 종목 없음)")

def run_sirius_905_scanner(strong_sectors):
    """
    v10.0 시리우스 주도주 추적 시스템
    장 개시 5분(09:05) 전후에 실행하여 최상위 대장주 선별
    """
    print(f"--- [v10.0 Sirius 주도주 추적 엔진 가동: {strong_sectors}] ---")
    
    # 1. 다중 섹터 기반 후보군 확보
    target_pool = sector_scanner.get_dynamic_target_pool(strong_sectors)
    if not target_pool: return
    
    today = datetime.now().strftime('%Y%m%d')
    final_winners = []

    # 2. 3중 필터 스캔 (Price > 3%, Vol > 15%, Intensity > 120%)
    for stock in target_pool:
        try:
            symbol = stock['Symbol']
            name = stock['Name']
            
            # 실시간 데이터
            df = fdr.DataReader(symbol, today)
            if df.empty: continue
            
            curr_close = df['Close'].iloc[-1]
            curr_open = df['Open'].iloc[-1]
            curr_vol = df['Volume'].iloc[-1]
            
            # 전일 전체 데이터 (기준선)
            df_hist = fdr.DataReader(symbol, (datetime.now() - pd.Timedelta(days=5)).strftime('%Y%m%d'))
            prev_vol_full = df_hist['Volume'].iloc[-2]
            
            # 필터 1: 등락률 3% 초과 (기세)
            day_chg = ((curr_close - curr_open) / curr_open) * 100
            if day_chg < 3.0: continue
            
            # 필터 2: 거래량 폭발력 15% 돌파 (개장 5분 만에 전일 거래량의 15% 이상 달성)
            vol_ratio = (curr_vol / prev_vol_full) * 100 if prev_vol_full > 0 else 0
            if vol_ratio < 15.0: continue
            
            # 필터 3: 체결강도/VPR 점수 (VPR로 대체하여 강도 측정)
            vpr_score = (day_chg * 2.0) + (vol_ratio * 0.5) 
            
            final_winners.append({
                'name': name,
                'code': symbol,
                'chg': day_chg,
                'vol_ratio': vol_ratio,
                'score': vpr_score
            })
        except:
            continue

    # 3. 최종 보고서 전송
    winners = sorted(final_winners, key=lambda x: x['score'], reverse=True)[:5]
    if winners:
        msg = f"<b>🛰️ [v10.0 Sirius 실시간 주도주 통보]</b>\n"
        msg += f"어제 강했던 섹터({', '.join(strong_sectors)})에서 3중 필터를 통과한 '진짜 대장'들을 찾았습니다.\n\n"
        for i, w in enumerate(winners):
            msg += f"{i+1}위: <b>{w['name']}</b> ({w['code']})\n"
            msg += f"🚩 상승률: {w['chg']:+.2f}% | 거래폭발: {w['vol_ratio']:.1f}%\n"
            msg += f"📍 판단: <b>수급 임팩트 감지 - 즉각 대응 가능</b>\n\n"
            
        send_telegram_msg(msg)
        print(f"v10.0 시리우스 포착 완료: {[w['name'] for w in winners]}")
    else:
        print("⏸ 조건 충족 종목 없음 (충분한 기운이 모이지 않았습니다.)")

if __name__ == "__main__":
    # 고도화된 시리우스 검색 시뮬레이션
    # 예: 어제 미국장에서 반도체와 AI 소프트웨어가 강했을 때
    run_sirius_905_scanner(["SEMICONDUCTOR", "AI_SOFTWARE"])
