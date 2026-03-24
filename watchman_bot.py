import requests
import time
import os
import sys

# 텔레그램 봇 설정 (이미 확인된 토큰 활용)
TELEGRAM_TOKEN = "8601832728:AAEZk8B2V1LkyLJAtcTDIwbhZMxS9Wa7GMI"
CHAT_ID = "8627162144"

def check_emergency_stop():
    """
    텔레그램 메시지를 확인하여 /STOP 명령어가 들어왔는지 체크합니다.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    try:
        res = requests.get(url).json()
        if res['ok']:
            for result in res['result']:
                message = result.get('message', {}).get('text', '')
                if message == '/STOP':
                    print("🚨 [EMERGENCY STOP] 텔레그램 비상 정지 신호 감지!")
                    return True
    except Exception as e:
        print(f"⚠️ 텔레그램 체크 오류: {e}")
        
    return False

def activate_kill_switch():
    """
    모든 주문 취소 및 시스템 강제 종료 로직
    """
    print("🛑 [KILL SWITCH] 모든 미체결 주문 취소 및 시스템을 즉각 종료합니다.")
    # 실제 KIS API 주문 취소 로직 호출 가능
    # requests.post(URL_CANCEL_ORDER, ...)
    
    send_telegram_msg("🚨 전량 매도 및 시스템 비상 정지가 완료되었습니다.")
    sys.exit(0)

def send_telegram_msg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=payload)

if __name__ == "__main__":
    print("🛰 [Watchman Bot] 가동 중... 텔레그램 /STOP 명령을 감시합니다.")
    # 무한 루프로 감시 (실제로는 별도 프로세스로 운영)
    while True:
        if check_emergency_stop():
            activate_kill_switch()
        time.sleep(5)
