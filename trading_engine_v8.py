import pandas as pd
import numpy as np
from datetime import datetime
import news_sentiment_analyzer
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_v8_watchman_engine():
    """
    슬리피지 마진 및 데이터 지연 보호가 적용된 v8.0 엔진
    """
    print(f"📡 [v8.0 'The Watchman' Active] {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-" * 60)

    # 1. 지연 속보 체크 (Latency Guard)
    news_info = news_sentiment_analyzer.get_news_sentiment()
    if news_info['status'] != 'OK':
        print("🚨 [CRITICAL] 데이터 지연 감지: 모든 자동 주문을 중단하고 Skip 모드로 전환합니다.")
        return

    # 2. 슬리피지 마진 설정 (Slippage Margin)
    # 9시 정각 체결 오차가 1.0%를 넘으면 위험 신호
    expected_price = 150000 
    current_market_price = 151800 # 실제 체결 시도 가격 (예시)
    
    slippage = ((current_market_price - expected_price) / expected_price) * 100
    SLIPPAGE_LIMIT = 1.0 # 1% 임계치
    
    print(f"▶ 예상가: {expected_price:,} | 현재가: {current_market_price:,}")
    print(f"▶ **슬리피지 오차: {slippage:+.2f}%** (제한: {SLIPPAGE_LIMIT}%)")

    if slippage > SLIPPAGE_LIMIT:
        print(f"⚠️ [SLIPPAGE ALERT] 오차가 너무 큽니다. 시장가 주문을 취소하고 지정가 하단 대기로 전환합니다.")
        # 주문 로직 변경 수행
    else:
        print("✅ 체결 오차 범위 내: 정상 주문 프로세스를 유지합니다.")

    # 3. 추격 손절(Trailing Stop) 설정
    high_price = 155000 # 장중 고점 기록
    current_price = 151800
    drawdown = ((current_price - high_price) / high_price) * 100
    TRAILING_STOP_LIMIT = -2.5 # 고점 대비 -2.5% 밀리면 던짐
    
    print(f"▶ 장중 고점: {high_price:,} | 현재가: {current_price:,}")
    print(f"▶ **고점 대비 하락(Drawdown): {drawdown:+.2f}%** (손절 기준: {TRAILING_STOP_LIMIT}%)")

    if drawdown <= TRAILING_STOP_LIMIT:
        print(f"🚨 [TRAILING STOP] 고점 대비 급락 포착! 전량 기계적 매도(Exit)를 실행합니다.")
    
    print("-" * 60)

if __name__ == "__main__":
    run_v8_watchman_engine()
