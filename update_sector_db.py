import FinanceDataReader as fdr
import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------------------
# 섹터 분류 키워드 정의
# ---------------------------------------------------------------------
SECTOR_KEYWORDS = {
    '반도체(HBM/장비)': ['반도체', 'HBM', '장비', '파운드리', '패키징', '낸드', 'DRAM'],
    '빅테크(AI/소프트웨어)': ['AI', '인공지능', '챗봇', 'LLM', '소프트웨어', '클라우드', 'SaaS'],
    '전기차(2차전지)': ['2차전지', '배터리', '양극재', '음극재', '리튬', '전기차', 'EV', '충전'],
    '의료AI/바이오': ['바이오', '제약', '신약', '임상', '헬스케어', '의료AI', '진단']
}

def get_news_keywords(stock_name):
    """네이버 뉴스에서 종목명으로 검색하여 헤드라인 키워드 수집"""
    url = f"https://search.naver.com/search.naver?where=news&query={stock_name}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        headlines = soup.select('.news_tit')
        text = " ".join([h.get_text() for h in headlines])
        return text
    except Exception as e:
        print(f"Error fetching news for {stock_name}: {e}")
        return ""

def update_db():
    print(f"--- [섹터 DB 자동 업데이트 시작 ({datetime.now()})] ---")
    
    # 1. 코스닥 거래대금 상위 200개 추출
    try:
        df_ksq = fdr.StockListing('KOSDAQ')
        top_200 = df_ksq.sort_values(by='Amount', ascending=False).head(200)
    except Exception as e:
        print(f"Listing error: {e}")
        return

    db = {sector: [] for sector in SECTOR_KEYWORDS.keys()}
    
    # 2. 각 종목별 뉴스 분석
    for idx, row in top_200.iterrows():
        name = row['Name']
        news_text = get_news_keywords(name)
        
        for sector, keywords in SECTOR_KEYWORDS.items():
            if any(kw in news_text for kw in keywords) or any(kw in name for kw in keywords):
                db[sector].append(name)
                print(f"[{sector}] 매핑 성공: {name}")
                break # 하나의 섹터에만 우선 매핑
        
        time.sleep(0.3) # 차단 방지

    # 3. 결과 저장
    with open('sector_db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    
    print("--- [업데이트 완료] sector_db.json 저장됨 ---")

if __name__ == "__main__":
    update_db()
