import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import sys
import io

# 윈도우 환경에서 한글 출력 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 나스닥 핵심 섹터 ETF 및 대표주 리스트 (전날 성과 확인용)
# 각 섹터별로 전날 미국 시장의 흐름을 파악하기 위한 종목들입니다.
nasdaq_watch_list = {
    '반도체(HBM/장비)': 'SOXX',
    '빅테크(AI/소프트웨어)': 'IGV',
    '전기차(2차전지)': 'TSLA',
    '빅테크(종합)': 'QQQ',
    '의료AI/바이오': 'IBB'
}

# 2. 국내 섹터별 '엣지' 종목 매핑 (나무 앱 테마 참고)
# 미국 시장의 특정 섹터가 강세를 보일 때 연관되어 움직일 수 있는 국내 종목들입니다.
korean_mapping = {
    '반도체(HBM/장비)': ['SK하이닉스', '한미반도체', '테크윙', '이오테크닉스', '가온칩스'],
    '빅테크(AI/소프트웨어)': ['NAVER', '카카오', '루닛', '코난테크놀로지', '이스트소프트'],
    '전기차(2차전지)': ['LG에너지솔루션', '에코프로비엠', '엘앤에프', '포스코퓨처엠'],
    '의료AI/바이오': ['삼성바이오로직스', '셀트리온', '알테오젠', '뷰노']
}

def get_nasdaq_performance():
    """
    미국 나스닥 주요 섹터의 전날 종가 기준 수익률을 계산합니다.
    """
    print(f"--- [미국장 마감 현황 ({datetime.now().strftime('%Y-%m-%d')})] ---")
    results = {}
    for sector, ticker in nasdaq_watch_list.items():
        # 최근 2일간의 데이터를 가져와서 전일 대비 변동률을 계산합니다.
        data = yf.Ticker(ticker).history(period='2d')
        if len(data) >= 2:
            change = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            results[sector] = round(change, 2)
            print(f"[{sector}] {ticker}: {change:+.2f}%")
    return results

def suggest_korean_stocks(nasdaq_results):
    """
    미국 시장의 성과를 바탕으로 오늘 아침 국내 시장에서 주목할 만한 종목을 추천합니다.
    """
    print("\n--- [오늘 아침 9시 국장 공략 섹터] ---")
    # 상승률 1.5% 이상인 섹터는 '급등 섹터'로 분류하여 관련 국내 종목을 보여줍니다.
    found_edge = False
    for sector, change in nasdaq_results.items():
        if change >= 1.5:
            # 윈도우 콘솔 호환을 위해 이모지 대신 텍스트로 변경
            print(f"[급등 섹터 발견]: {sector} ({change}%)")
            print(f"-> 관심 종목: {', '.join(korean_mapping.get(sector, []))}")
            print("-" * 30)
            found_edge = True
        # 하락폭이 큰 섹터는 주의 메시지를 출력합니다.
        elif change <= -1.5:
            print(f"[하락 주의]: {sector} ({change}%) - 시초가 조심!")
    
    if not found_edge:
        print("뚜렷한 급등 섹터가 발견되지 않았습니다. 관망을 권장합니다.")

if __name__ == "__main__":
    # 1. 미국장 마감 현황 파악
    perf = get_nasdaq_performance()
    # 2. 결과에 따른 국내 종목 추천
    suggest_korean_stocks(perf)
