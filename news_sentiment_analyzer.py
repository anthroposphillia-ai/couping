import requests
from bs4 import BeautifulSoup
import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_news_sentiment():
    """
    로이터/블룸버그 주요 헤드라인을 스캔하여 트럼프, 연준, 전쟁 관련 감성 점수를 산출합니다.
    """
    print("--- [글로벌 뉴스 감성 분석 시작] ---")
    
    # 실제 운영 시에는 로이터/블룸버그 RSS나 API를 사용하지만, 
    # 여기서는 검색 결과를 기반으로 한 가상 분석 로직을 구현합니다. (검색 도구 활용 예정)
    
    # 분석 키워드 정의
    keywords = {
        'trump': {'weight': 1.5, 'pos': ['tax cut', 'deregulation', 'stimulus'], 'neg': ['tariff', 'trade war', 'sanction']},
        'fed': {'weight': 2.0, 'pos': ['rate cut', 'dovish', 'easing'], 'neg': ['rate hike', 'hawkish', 'inflation']},
        'war': {'weight': 2.5, 'pos': ['ceasefire', 'peace', 'negotiation'], 'neg': ['invasion', 'escalation', 'strike']}
    }
    
    # [시뮬레이션 데이터] 실제 상황에서는 search_web 결과를 파싱하여 사용
    sample_headlines = [
        "Trump warns of new 60% tariffs on Chinese goods",
        "Fed Chair Powell signals potential rate cut in September",
        "Middle East tensions escalate as ceasefire talks stall"
    ]
    
    sentiment_score = 0
    detected_events = []

    for headline in sample_headlines:
        lower_h = headline.lower()
        for key, config in keywords.items():
            if key in lower_h:
                # 긍정 단어 체크
                for p in config['pos']:
                    if p in lower_h:
                        sentiment_score += 10 * config['weight']
                        detected_events.append(f"🟢 {key.upper()}: {p}")
                # 부정 단어 체크
                for n in config['neg']:
                    if n in lower_h:
                        sentiment_score -= 15 * config['weight']
                        detected_events.append(f"🔴 {key.upper()}: {n}")

    # -50 ~ +50 범위 제한
    final_score = max(-50, min(50, sentiment_score))
    
    print(f"▶ 탐지된 주요 이슈: {', '.join(detected_events) if detected_events else '특이사항 없음'}")
    print(f"▶ 뉴스 감성 온도: {final_score:+.1f}도")
    
    return {
        'score': final_score,
        'events': detected_events
    }

if __name__ == "__main__":
    get_news_sentiment()
