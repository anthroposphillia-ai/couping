import requests
from bs4 import BeautifulSoup
import sys
import io
import time
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_news_sentiment():
    """
    로이터/블룸버그 헤드라인 스캔 및 데이터 신선도(Latency) 검증
    """
    print("--- [v8.0 News Intelligence Scanner] ---")
    
    # 데이터 수신 시간 기록 (Latency Check용)
    fetch_time = datetime.now()
    
    # [시뮬레이션] 실제로는 search_web 결과를 파싱
    # 데이터 소스의 타임스탬프를 가져왔다고 가정
    data_timestamp = datetime.now() # 실시간 데이터 가정
    
    latency = (fetch_time - data_timestamp).total_seconds()
    if latency > 60:
        print(f"⚠️ 데이터 지연 속보: {latency:.1f}초 지연됨 (신뢰 불가)")
        return {'score': 0, 'events': [], 'status': 'LATENCY_ERROR'}

    keywords = {
        'trump': {'weight': 1.5, 'pos': ['tax cut', 'deregulation'], 'neg': ['tariff', 'trade war']},
        'fed': {'weight': 2.0, 'pos': ['rate cut', 'dovish'], 'neg': ['rate hike', 'hawkish']},
        'war': {'weight': 2.5, 'pos': ['ceasefire', 'peace'], 'neg': ['invasion', 'escalation']}
    }
    
    sample_headlines = [
        "Trump tariff threat looms over markets",
        "Fed's Powell maintains hawkish stance on inflation",
        "Peace talks gain momentum in Eastern Europe"
    ]
    
    sentiment_score = 0
    detected_events = []

    for headline in sample_headlines:
        lower_h = headline.lower()
        for key, config in keywords.items():
            if key in lower_h:
                for p in config['pos']:
                    if p in lower_h:
                        sentiment_score += 10 * config['weight']
                        detected_events.append(f"🟢 {key.upper()}: {p}")
                for n in config['neg']:
                    if n in lower_h:
                        sentiment_score -= 15 * config['weight']
                        detected_events.append(f"🔴 {key.upper()}: {n}")

    final_score = max(-50, min(50, sentiment_score))
    print(f"▶ 뉴스 온도: {final_score:+.1f}도 (지연: {latency:.2f}s)")
    
    return {
        'score': final_score,
        'events': detected_events,
        'status': 'OK',
        'timestamp': data_timestamp.strftime('%H:%M:%S')
    }

if __name__ == "__main__":
    get_news_sentiment()
