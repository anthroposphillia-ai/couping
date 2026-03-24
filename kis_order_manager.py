import requests
import json
import kis_auth

URL_BASE = "https://openapivts.koreainvestment.com:29443" # 모의투자 서버

def place_buy_order(stock_code, qty, price="0"):
    """
    주식 매수 주문을 실행합니다. (시장가 기준 시뮬레이션)
    """
    token = kis_auth.get_access_token()
    if not token: return
    
    path = "/uapi/domestic-stock/v1/trading/order-cash"
    url = f"{URL_BASE}{path}"
    
    # KIS API 필수 헤더 설정
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": kis_auth.APP_KEY,
        "appsecret": kis_auth.APP_SECRET,
        "tr_id": "VTTC0802U", # 모의투자 주식 현금 매수 주문 ID
        "custtype": "P"
    }
    
    # 주문 데이터 설정 (시장가 매수 예시)
    payload = {
        "CANO": "본인의_계좌번호_8자리", # 앞 8자리
        "ACNT_PRDT_CD": "01", # 상품코드 뒤 2자리
        "PDNO": stock_code,
        "ORD_DVSN": "01", # 01: 시장가
        "ORD_QTY": str(qty),
        "ORD_UNPR": "0" 
    }
    
    print(f"--- [KIS 자동 주문 실행: {stock_code}] ---")
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if res.status_code == 200:
        res_data = res.json()
        if res_data['rt_cd'] == '0':
            print(f"🚀 주문 성공: {res_data['msg1']}")
            return True
        else:
            print(f"⚠️ 주문 실패: {res_data['msg1']} ({res_data['rt_cd']})")
    else:
        print(f"❌ API 오류: {res.text}")
    
    return False

if __name__ == "__main__":
    # 테스트 매수 (삼성전자 1주 시장가)
    place_buy_order("005930", 1)
