import requests
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime
import time
import sys
import io
import os
import technical_analyzer
import supply_demand_tracer
import market_regime_analyzer
import trading_journal

# 윈도우 환경에서 한글 출력 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------------------------------------------------------------------
# 1. 설정 정보 (텔레그램 및 통계) - GitHub Secrets 우선 순위
# ---------------------------------------------------------------------
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8601832728:AAEZk8B2V1LkyLJAtcTDIwbhZMxS9Wa7GMI")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "8627162144")

# 백테스팅 기반 핵심 통계
WIN_RATE_SOXX = "67.57%"
GAP_BLUE_PROB = "75.00%" # 갭 3% 이상 시 음봉 확률

nasdaq_watch_list = {
    '반도체(HBM/장비)': 'SOXX',
    '빅테크(AI/소프트웨어)': 'IGV',
    '전기차(2차전지)': 'TSLA'
}

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def get_briefing():
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    report = f" [투자 전략 고도화 브리핑 - {now_str}] \n\n"
    
    # 1. 시장 지표 수집
    nq_f = yf.Ticker("NQ=F").history(period='2d')
    f_chg = ((nq_f['Close'].iloc[-1] - nq_f['Close'].iloc[-2]) / nq_f['Close'].iloc[-2]) * 100
    
    fx = yf.Ticker("KRW=X").history(period='2d')
    fx_now = fx['Close'].iloc[-1]
    fx_chg = ((fx['Close'].iloc[-1] - fx['Close'].iloc[-2]) / fx['Close'].iloc[-2]) * 100
    
    # 2. 진입 점수 및 리스크 필터링
    score = 100
    if f_chg < -0.5: score -= 30
    if fx_chg > 0.3: score -= 20
    
    # [v4.0 핵심] 시장 성격(Regime) 분석
    regime_info = market_regime_analyzer.analyze_market_regime("KS11")
    
    # [v2.0 핵심] 시가 고가(설거지) 회피 로직
    simulated_gap = 3.5 if f_chg > 1.5 else 1.2
    
    report += f"▶ 나스닥 선물: {f_chg:+.2f}%\n"
    report += f"▶ 원/달러 환율: {fx_now:,.1f}원\n"
    report += f"▶ **오늘의 진입 점수: {score}점**\n"
    
    if regime_info:
        report += f"▶ **시장 기세(Regime): {regime_info['status_msg']}**\n"
        report += f"▶ **추천 비중: {regime_info['exposure_ratio']}%**\n\n"

    if f_chg > 1.5 and simulated_gap >= 3.0:
        report += f"🚨 **[강력 경고] 시가 고가 위험 포착**\n"
        report += f"현재 나스닥 영향으로 갭 상승({simulated_gap}%)이 예상되나, "
        report += f"갭 3% 이상 시 성적은 **{GAP_BLUE_PROB} 확률로 음봉(하락)**이었습니다.\n"
        report += "👉 **절대 추격 매수 금지! 10시 이후 눌림목 확인 필수.**\n\n"
    else:
        if score >= 80: report += "✅ 적극 공략 가능 장세\n"
        else: report += "⚠️ 보수적 접근 권장\n"
    
    report += f"\n[통계 엣지] SOXX 2%↑ 시 삼성전자 승률 {WIN_RATE_SOXX}\n"
    
    # 4. [v3.0 신규] 실시간 수급 및 기술적 분석 결합
    investor_status = supply_demand_tracer.get_investor_estimated_trend()
    tech_info = technical_analyzer.analyze_technical_indicators("005930") # 삼성전자 기준
    
    report += "\n--- [v3.0 입체 분석: 수급 & 차트] ---\n"
    if investor_status:
        report += f"📊 외인/기관 수급: {investor_status['warning']}\n"
    
    if tech_info:
        report += f"📈 기술적 위치: {tech_info['status']} (돌파확률 {tech_info['breakout_prob']}%)\n"
        report += f"📉 매물대 저항: {tech_info['resistance']:,.0f}원 까지 {((tech_info['resistance']-tech_info['price'])/tech_info['price']*100):+.2f}%\n"

    # 3. 매매 일지 기록
    prediction_data = {
        'score': score,
        'futures_change': f_chg,
        'simulated_gap': simulated_gap,
        'breakout_prob': tech_info['breakout_prob'] if tech_info else 0,
        'action': "AVOID_GAP" if simulated_gap >= 3.0 else "ENTRY_OK"
    }
    trading_journal.save_morning_prediction(prediction_data)
    
    report += "\n* 이 리포트는 GitHub Actions를 통해 무중단 전송됩니다."
    return report

if __name__ == "__main__":
    briefing = get_briefing()
    print(briefing)
    send_telegram_msg(briefing)
