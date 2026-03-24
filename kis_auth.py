import requests
import json
import os
import time

# KIS API 설정 (모의투자 서버 기준)
APP_KEY = os.getenv("KIS_APP_KEY", "본인의_앱키를_입력하세요")
APP_SECRET = os.getenv("KIS_APP_SECRET", "본인의_시크릿을_입력하세요")
URL_BASE = "https://openapivts.koreainvestment.com:29443"

# 토큰 캐싱을 위한 전역 변수
_ACCESS_TOKEN = None
_TOKEN_EXPIRE_TIME = 0

def get_access_token():
    """
    한국투자증권 API 접근 토큰을 발급/갱신합니다. (만료 10분 전 자동 갱신)
    """
    global _ACCESS_TOKEN, _TOKEN_EXPIRE_TIME
    
    current_time = time.time()
    
    # 토큰이 유효하면 기존 토큰 반환 (만료 10분 전 여유 유지)
    if _ACCESS_TOKEN and current_time < _TOKEN_EXPIRE_TIME - 600:
        return _ACCESS_TOKEN

    print("🔄 KIS API 토큰 갱신 중...")
    path = "/oauth2/tokenP"
    url = f"{URL_BASE}{path}"
    
    headers = {"content-type": "application/json"}
    payload = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if res.status_code == 200:
        data = res.json()
        _ACCESS_TOKEN = data.get('access_token')
        # expires_in은 보통 86400초(24시간)
        expires_in = int(data.get('expires_in', 86400))
        _TOKEN_EXPIRE_TIME = current_time + expires_in
        print("✅ KIS API 인증 성공: 토큰 발급 완료")
        return _ACCESS_TOKEN
    else:
        print(f"❌ KIS API 인증 실패: {res.text}")
        return None

if __name__ == "__main__":
    get_access_token()
