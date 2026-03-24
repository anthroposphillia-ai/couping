import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_investor_estimated_trend():
    """
    네이버 금융에서 외국인/기관 수급 잠정치(장중)를 파악합니다.
    (실제 구현 시 주기적인 크롤링이나 전문 API 연동 권장)
    """
    print("--- [장중 수급 잠성치 추적 시작] ---")
    
    # 네이버 코스피 투자자별 매매동향 잠정치 (예시 URL)
    url = "https://finance.naver.com/sise/investor_deal_info.naver"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 실제로는 테이블 내 '잠정치' 텍스트를 파싱해야 함
        # 여기서는 프로토타입으로 수급의 '뱡향성'을 감지하는 로직을 시뮬레이션함
        # 장중(9:10~9:20)에는 외인/기관의 순매수 합계를 확인
        
        # [시뮬레이션 데이터] 실제 상황에선 파싱된 정수 사용
        foreigner_net = -500 # 억 단위 (매도세 가정)
        institution_net = -200 # 억 단위 (매도세 가정)
        
        is_double_sell = (foreigner_net < 0 and institution_net < 0)
        
        status = {
            'foreigner': foreigner_net,
            'institution': institution_net,
            'is_double_sell': is_double_sell,
            'warning': "🚨 외인/기관 쌍끌이 매도 포착! 속임수 반등 주의" if is_double_sell else "✅ 수급 양호"
        }
        
        print(f"▶ 외국인: {foreigner_net}억 | 기관: {institution_net}억")
        print(f"▶ 상태: {status['warning']}")
        
        return status
    except Exception as e:
        print(f"수급 추적 오류: {e}")
        return None

if __name__ == "__main__":
    get_investor_estimated_trend()
