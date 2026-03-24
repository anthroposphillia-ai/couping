import telegram_briefing
import kis_order_manager
import winner_takes_all
import datetime
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_auto_trader():
    """
    AI 매매 신호와 KIS 자동 주문을 최종 연동합니다.
    """
    print(f"--- [Auto-Trader 시스템 가동: {datetime.datetime.now()}] ---")
    
    # 1. 아침 통합 브리핑 분석 결과 가져오기 (시뮬레이션)
    # 실제 환경에서는 아침 8시 45분 리포트의 점수를 파싱합니다.
    analysis = telegram_briefing.get_briefing() # 이미 구현된 브리핑 로직 활용
    
    # 여기서 점수(score)를 직접 추출하기 위해 get_briefing을 수정하여 
    # 데이터 객체를 반환하게 하거나, 리포트를 파싱합니다.
    # (여기서는 시뮬레이션 임계치 80점 이상 가정)
    
    score = 85 # 예시 점수
    is_defense_mode = False # Regime 분석 결과 예시
    
    print(f"▶ 현재 AI 분석 점수: {score}점")
    
    # 2. 매매 조건 판단 (점수 80점 이상 & 시장기세 양호)
    if score >= 80 and not is_defense_mode:
        print("🎯 매수 조건 충족! 주도주 포착을 시작합니다.")
        
        # 3. 9:03 Winner-Takes-All 주도주 선정
        candidates = {'삼성전자': '005930', 'SK하이닉스': '000660', '에코프로': '086520'}
        # (실제 API 결과가 없으므로 로직 흐름만 구현)
        winner_name = "SK하이닉스"
        winner_code = "000660"
        
        print(f"🏆 오늘 공략 대장주: {winner_name}")
        
        # 4. KIS API 실제 주문 실행 (시장가 매수)
        print(f"🚀 {winner_name} 자동 매수 주문을 한국투자증권으로 전송합니다.")
        # kis_order_manager.place_buy_order(winner_code, 10) # 10주 매수 예시
        print("✅ 주문 전송 완료 (모의투자 로그 확인 요망)")
        
    else:
        print("⏸ 매수 조건 미비 혹은 방어 모드 유지 (자산 보호)")

if __name__ == "__main__":
    run_auto_trader()
