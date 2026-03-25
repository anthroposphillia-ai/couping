import FinanceDataReader as fdr
import pandas as pd

# MASTER_SECTOR_KEYWORDS (v9.5) - 글로벌 동조화 DB
MASTER_SECTOR_KEYWORDS = {
    "SEMICONDUCTOR": {
        "title": "반도체/장비/소부장",
        "keywords": ["HBM", "온디바이스", "CXL", "유리기판", "OSAT", "후공정", "보호회로", "패키징", "테스트", "본딩", "EUV", "팹리스", "디자인하우스", "반도체"],
        "us_match": ["SOXX", "NVDA", "MU", "AMAT", "ASML"]
    },
    "SECONDARY_BATTERY": {
        "title": "2차전지/소재/충전",
        "keywords": ["양극재", "음극재", "전해액", "분리막", "전고체", "폐배터리", "리튬", "니켈", "충전소", "ESS", "실리콘음극재", "동박", "LFP"],
        "us_match": ["TSLA", "ALB", "RIVN", "LCID"]
    },
    "AI_SOFTWARE": {
        "title": "AI/소프트웨어/보안",
        "keywords": ["LLM", "생성형AI", "챗봇", "클라우드", "SaaS", "데이터센터", "보안", "양자암호", "인공지능", "빅데이터", "플랫폼"],
        "us_match": ["MSFT", "GOOGL", "PLTR", "META", "CRM"]
    },
    "ROBOTICS": {
        "title": "로봇/자동화/기계",
        "keywords": ["협동로봇", "감속기", "서보모터", "액추에이터", "AMR", "AGV", "물류자동화", "스마트팩토리", "웨어러블", "로봇"],
        "us_match": ["ISRG", "TER", "ABB"]
    },
    "BIO_HEALTHCARE": {
        "title": "바이오/제약/의료AI",
        "keywords": ["임상", "신약", "바이오시밀러", "면역항암제", "ADC", "유전자", "CDMO", "의료AI", "디지털헬스케어", "비만치료제"],
        "us_match": ["IBB", "XBI", "LLY", "NVO"]
    },
    "AUTOMOTIVE": {
        "title": "자동차/부품/자율주행",
        "keywords": ["자율주행", "ADAS", "Lidar", "전장", "와이어링하네스", "모터", "조향", "전동화", "수소차"],
        "us_match": ["TSLA", "GM", "F", "MBLY"]
    }
}

def get_sector_pool(category_id):
    """
    v9.5: 마스터 DB 기반 동적 종목 풀 생성
    """
    if category_id not in MASTER_SECTOR_KEYWORDS:
        print(f"🔍 [Sector Scanner] '{category_id}' 일반 키워드 검색 중...")
        keywords = [category_id]
        title = category_id
    else:
        config = MASTER_SECTOR_KEYWORDS[category_id]
        keywords = config['keywords']
        title = config['title']
        print(f"🔍 [Sector Scanner] '{title}' 섹터 분석 중 (관련 키워드 {len(keywords)}개)...")

    # 1. KRX 전 종목 리스팅
    try:
        df_krx = fdr.StockListing('KRX')
    except Exception as e:
        print(f"❌ 종목 리스트 불러오기 실패: {e}")
        return []

    # 2. 다중 키워드 매칭 (Regex 최적화)
    regex_pattern = '|'.join(keywords)
    sector_pool = df_krx[df_krx['Name'].str.contains(regex_pattern, case=False, na=False)].copy()

    # 3. 거래대금 상위 필터링 및 정리
    if not sector_pool.empty and 'Amount' in sector_pool.columns:
        sector_pool = sector_pool.sort_values(by='Amount', ascending=False).head(100)

    sector_pool = sector_pool.rename(columns={'Code': 'Symbol'})
    
    # 9.5 추가: 미국 매칭 정보 포함
    symbol_list = sector_pool[['Symbol', 'Name']].to_dict('records')
    print(f"✅ 스캔 완료: {len(symbol_list)}개 종목 발견")
    
    return {
        'title': title,
        'symbols': symbol_list,
        'us_match': MASTER_SECTOR_KEYWORDS.get(category_id, {}).get('us_match', [])
    }

def get_dynamic_target_pool(strong_sectors):
    """
    미국장에서 강했던 섹터(리스트)를 입력받아 국내 전 종목 중 통합 후보군 추출
    """
    print(f"🔍 [Sirius Scanner] 강세 섹터 {strong_sectors} 기반 동적 풀 구성 중...")
    
    # 1. KRX 전 종목 리스팅
    try:
        df_krx = fdr.StockListing('KRX')
    except Exception as e:
        print(f"❌ 종목 리스트 불러오기 실패: {e}")
        return []

    total_pool = []
    for sector_key in strong_sectors:
        config = MASTER_SECTOR_KEYWORDS.get(sector_key)
        if not config: continue
        
        # 키워드 그물질 (Regex 최적화)
        pattern = '|'.join(config['keywords'])
        # Name 기반 검색 (Sector 정보 부재 대응)
        filtered = df_krx[df_krx['Name'].str.contains(pattern, na=False, case=False)]
        
        # Symbol로 컬럼 처리 (renaming 'Code' if needed)
        filtered = filtered.rename(columns={'Code': 'Symbol'})
        total_pool.extend(filtered[['Symbol', 'Name']].to_dict('records'))
    
    # 중복 종목 제거 (Symbol 기준)
    unique_pool = {v['Symbol']: v for v in total_pool}.values()
    print(f"✅ 동적 풀 구성 완료: {len(unique_pool)}개 종목 확보")
    
    return list(unique_pool)

    # 3. [초정밀 필터] 관리종목, 우선주 등 제외 및 시가총액 하위(예: 500억 이하) 제외 권장
    # (여기서는 기본 필터만 적용)
    
    symbol_list = sector_pool[['Symbol', 'Name']].to_dict('records')
    print(f"✅ 스캔 완료: {len(symbol_list)}개 종목 발견")
    
    return symbol_list

if __name__ == "__main__":
    # 테스트 실행
    pool = get_sector_pool("반도체")
    for s in pool[:5]:
        print(f"▶ {s['Name']} ({s['Symbol']})")
