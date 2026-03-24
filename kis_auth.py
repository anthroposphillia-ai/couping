import requests
import json
import os

# KIS API 설정 (모의투자 서버 기준)
# 보안을 위해 AppKey와 Secret은 환경변수로 관리하는 것을 권장합니다.
APP_KEY = os.getenv("KIS_APP_KEY", "본인의_앱키를_입력하세요")
APP_SECRET = os.getenv("KIS_APP_SECRET", "본인의_시크릿을_입력하세요")
URL_BASE = "https://openapivts.koreainvestment.com:29443" # 모의투자 서버

def get_access_token():
    """
    한국투자증권 API 접근 토큰을 발급받습니다.
    """
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
        token = res.json().get('access_token')
        print("✅ KIS API 인증 성공: 토큰 발급 완료")
        return token
    else:
        print(f"❌ KIS API 인증 실패: {res.text}")
        return None

if __name__ == "__main__":
    get_access_token()
