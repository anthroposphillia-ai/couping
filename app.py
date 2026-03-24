import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import json
import os
import subprocess

# ---------------------------------------------------------------------
# 1. 환경 설정 및 초기화
# ---------------------------------------------------------------------
st.set_page_config(page_title="Global Trading Edge Dashboard", layout="wide")

# 나스닥 핵심 섹터 ETF 가이드
nasdaq_watch_list = {
    '반도체(HBM/장비)': 'SOXX',
    '빅테크(AI/소프트웨어)': 'IGV',
    '전기차(2차전지)': 'TSLA',
    '빅테크(종합)': 'QQQ',
    '의료AI/바이오': 'IBB'
}

@st.cache_data(ttl=3600)
def load_sector_db():
    """저장된 섹터 DB를 불러오거나 기본값을 반환"""
    db_path = 'sector_db.json'
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # 기본값 (DB가 없을 경우)
    return {
        '반도체(HBM/장비)': ['SK하이닉스', '한미반도체', '테크윙'],
        '빅테크(AI/소프트웨어)': ['NAVER', '카카오', '루닛'],
        '전기차(2차전지)': ['LG에너지솔루션', '에코프로비엠', '엘앤에프'],
        '의료AI/바이오': ['삼성바이오로직스', '셀트리온', '알테오젠']
    }

@st.cache_data(ttl=3600)
def update_korean_mapping():
    """코스닥 거래대금 상위 종목과 섹터 DB를 병합하여 매핑"""
    try:
        df_ksq = fdr.StockListing('KOSDAQ')
        top_100 = df_ksq.sort_values(by='Amount', ascending=False).head(100)
        
        # 저장된 DB 불러오기
        db = load_sector_db()
        
        # 현재 상위 종목 중 DB에 있는 것들 위주로 필터링 (동적 업데이트 느낌)
        current_mapping = {sector: [] for sector in db.keys()}
        top_names = top_100['Name'].tolist()
        
        for sector, stocks in db.items():
            # DB에 있는 종목 중 현재 거래대금 상위 100위 안에 있는 종목 우선 표시
            for s in stocks:
                if s in top_names:
                    current_mapping[sector].append(s)
            
            # 상위 100위 안에는 없지만 DB에는 있는 종목 중 일부 추가 (추천용)
            if len(current_mapping[sector]) < 3:
                current_mapping[sector].extend([s for s in stocks if s not in current_mapping[sector]])
                current_mapping[sector] = current_mapping[sector][:5] # 최대 5개 유지
                
        return current_mapping, top_100
    except Exception as e:
        st.error(f"국내 종목 매핑 업데이트 실패: {e}")
        return load_sector_db(), pd.DataFrame()

# ---------------------------------------------------------------------
# 2. 데이터 크롤링 및 처리 함수
# ---------------------------------------------------------------------

@st.cache_data(ttl=600)
def get_nasdaq_market_data():
    """나스닥 현물, 선물 및 환율 정보 수집"""
    data_results = {}
    try:
        # 1. 나스닥 선물 (NQ=F)
        nq_f = yf.Ticker("NQ=F").history(period='2d')
        if len(nq_f) >= 2:
            futures_chg = ((nq_f['Close'].iloc[-1] - nq_f['Close'].iloc[-2]) / nq_f['Close'].iloc[-2]) * 100
            futures_price = nq_f['Close'].iloc[-1]
            data_results['futures'] = {'price': futures_price, 'change': futures_chg}
        
        # 2. 원/달러 환율 (KRW=X)
        usdkrw = yf.Ticker("KRW=X").history(period='2d')
        if len(usdkrw) >= 2:
            fx_price = usdkrw['Close'].iloc[-1]
            fx_prev = usdkrw['Close'].iloc[-2]
            fx_chg = ((fx_price - fx_prev) / fx_prev) * 100
            data_results['fx'] = {'price': fx_price, 'change': fx_chg}

        # 3. 섹터별 성과
        sector_results = {}
        for sector, ticker in nasdaq_watch_list.items():
            data = yf.Ticker(ticker).history(period='2d')
            if len(data) >= 2:
                change = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
                sector_results[sector] = round(change, 2)
        data_results['sectors'] = sector_results
        
        return data_results
    except Exception as e:
        st.error(f"데이터 수집 중 오류 발생: {e}")
        return None

# ---------------------------------------------------------------------
# 3. 사이드바 구성
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 관리자 설정")
    if st.button("🔄 섹터 DB 자동 업데이트 (4PM)"):
        with st.spinner("뉴스 분석 중... (약 1분 소요)"):
            try:
                subprocess.run(["python", "update_sector_db.py"], check=True)
                st.success("섹터 DB 업데이트 완료!")
                st.cache_data.clear() # 캐시 초기화
                st.rerun()
            except Exception as e:
                st.error(f"업데이트 중 오류 발생: {e}")
    st.info("거래대금 상위 200개 종목의 뉴스를 분석하여 섹터를 정교화합니다.")

# ---------------------------------------------------------------------
# 4. 메인 레이아웃 구성
# ---------------------------------------------------------------------

st.title("🚀 Global Trading Edge Dashboard")
st.markdown(f"**기준 시간:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 데이터 로딩
market_data = get_nasdaq_market_data()
if market_data:
    futures = market_data['futures']
    fx = market_data['fx']
    sector_perf = market_data['sectors']
    korean_mapping, top_df = update_korean_mapping()

    # 상단 지수 현황 (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="나스닥 선물 (NQ=F)", value=f"{futures['price']:,.2f}", delta=f"{futures['change']:+.2f}%")
    with col2:
        st.metric(label="원/달러 환율 (USDKRW)", value=f"{fx['price']:,.1f}원", delta=f"{fx['change']:+.2f}%")
    with col3:
        qqq_chg = sector_perf.get('빅테크(종합)', 0.0)
        st.metric(label="나스닥 현물 (QQQ)", value="QQQ", delta=f"{qqq_chg:+.2f}%")

    st.divider()

    # [1단계] 아침 8시 30분 전략 알림 섹션
    st.divider()
    st.subheader("🎯 오늘의 국장 매매 전략 점수")
    
    # 점수 계산 로직 (사용자 제안 반영)
    sentiment_score = 100
    if futures['change'] < -0.5: sentiment_score -= 30
    if fx['change'] > 0.3: sentiment_score -= 20
    if fx['price'] >= 1350: sentiment_score -= 10 # 환율 절대치 경고 추가
    
    # 점수별 색상 및 메시지 결정
    if sentiment_score >= 80:
        score_color = "green"
        action_msg = "✅ **적극 공략**: 나스닥 상승 + 선물 견조 + 환율 안정"
    elif sentiment_score >= 50:
        score_color = "orange"
        action_msg = "⚠️ **보수적 접근**: 시초가 형성 후 눌림목 확인 필요"
    else:
        score_color = "red"
        action_msg = "🚨 **진입 금지**: 나스닥 상승분을 선물/환율이 깎아먹는 중"
    
    col_score, col_msg = st.columns([1, 2])
    with col_score:
        st.markdown(f"<h1 style='text-align: center; color: {score_color};'>{sentiment_score}점</h1>", unsafe_allow_html=True)
    with col_msg:
        st.markdown(f"### {action_msg}")
    
    st.markdown("---")
    st.subheader("⚠️ 시장 모니터링 & 대응 전략")
    now = datetime.now()
    
    # 전략 분석 로직
    # 1. 나스닥 선물 하락 필터링
    if futures['change'] <= -0.5:
        st.warning("🚨 [주의] 나스닥 선물 급락 중! 국장 시초가 '시고저저' 가능성이 매우 높습니다. 무리한 추격 매수 금지.")
    elif sector_perf.get('빅테크(종합)', 0.0) > 0 and futures['change'] < 0:
        st.warning(f"⚠️ [주의] 미국장은 {sector_perf.get('빅테크(종합)', 0.0):+.2f}% 상승 마감했으나, 현재 선물이 하락 중입니다. 국장 갭상승 후 눌림목 주의!")
    
    # 2. 환율 급등 필터링
    if fx['change'] >= 0.5 or fx['price'] >= 1350: # 예시 임계치
        st.error(f"💵 [경고] 환율 급등 중({fx['price']:,.1f}원). 외국인 대량 매도세 출현 가능성이 높습니다.")
    
    # 3. [2단계] 저평가 스캐너 (나스닥 vs 국장 예상치 - 시뮬레이션)
    st.markdown("---")
    st.subheader("🔍 오늘의 저평가 스캐너 (Gap 분석 엣지)")
    
    # 가상의 예상 체결 등락률 생성 (현재 등락률을 기반으로 엣지 계산 예시)
    edge_data = []
    for sector, nasdaq_chg in sector_perf.items():
        stocks = korean_mapping.get(sector, [])
        if stocks:
            # 첫 번째 종목을 대표로 등락률 가져오기 (실제로는 장전 예상 등락률 필요)
            stock_name = stocks[0]
            stock_info = top_df[top_df['Name'] == stock_name]
            
            if not stock_info.empty:
                kor_chg = stock_info['ChagesRatio'].iloc[0]
                gap = nasdaq_chg - kor_chg # 엣지 계산
                
                status = "🟢 매수 우위" if gap > 1.0 else "⚪ 관망"
                if gap < -1.0: status = "🔴 과열 주의"
                
                edge_data.append({
                    "섹터": sector,
                    "나스닥(A)": f"{nasdaq_chg:+.2f}%",
                    "국내대표(B)": f"{stock_name} ({kor_chg:+.2f}%)",
                    "엣지(A-B)": f"{gap:+.2f}%",
                    "판단": status
                })
    
    if edge_data:
        st.table(pd.DataFrame(edge_data))
    else:
        st.write("분석할 수 있는 상위 종목 데이터가 부족합니다.")

    st.divider()

    # 섹터 상세 성과 및 관련주
    st.subheader("🔥 미국 섹터 성과 & 국장 대응 전략")
    cols = st.columns(len(sector_perf))

    for i, (sector, change) in enumerate(sector_perf.items()):
        with cols[i]:
            color = "red" if change > 0 else "blue"
            st.markdown(f"### {sector}")
            st.markdown(f"<h2 style='color: {color};'>{change:+.2f}%</h2>", unsafe_allow_html=True)
            
            # 국장 대응 종목 표시
            related_stocks = korean_mapping.get(sector, [])
            if related_stocks:
                st.info(f"👉 **관심 국장 종목**\n\n" + ", ".join(related_stocks))
            else:
                st.write("관련 상위 종목 없음")

    st.divider()

    # 코스닥 거래대금 상위 리스트 (참고용)
    st.subheader("💰 코스닥 실시간 거래대금 상위 (TOP 10)")
    st.table(top_df[['Name', 'Close', 'ChagesRatio', 'Amount']].head(10).style.format({'Amount': '{:,.0f}'}))

    # 차트 시각화
    fig = go.Figure(go.Bar(
        x=list(sector_perf.keys()),
        y=list(sector_perf.values()),
        marker_color=['red' if x > 0 else 'blue' for x in sector_perf.values()]
    ))
    fig.update_layout(title="나스닥 섹터별 등락률 비교", yaxis_title="변동률(%)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("데이터를 불러오는 중입니다...")
