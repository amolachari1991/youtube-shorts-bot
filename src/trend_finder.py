import requests
from pytrends.request import TrendReq
import google.generativeai as genai
import os
import json
from datetime import datetime, timedelta

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def get_google_trends():
    """Get trending topics from Google Trends India"""
    try:
        pytrends = TrendReq(hl='hi-IN', tz=330)
        trending = pytrends.trending_searches(pn='india')
        topics = trending[0].tolist()[:10]
        print(f"Google Trends found: {topics[:5]}")
        return topics
    except Exception as e:
        print(f"Google Trends error: {e}")
        return []

def get_news_topics():
    """Get trending news from India"""
    try:
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            "country": "in",
            "apiKey": NEWS_API_KEY,
            "pageSize": 20,
            "language": "hi"
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        topics = []
        if data.get("articles"):
            for article in data["articles"]:
                if article.get("title"):
                    topics.append(article["title"])
        
        print(f"News topics found: {len(topics)}")
        return topics
    except Exception as e:
        print(f"News API error: {e}")
        return []

def get_youtube_trends():
    """Get trending YouTube topics India"""
    try:
        url = "https://www.youtube.com/feed/trending"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        topics = []
        if "trending" in response.text.lower():
            topics.append("trending india today")
        
        return topics
    except Exception as e:
        print(f"YouTube trends error: {e}")
        return []

def score_topic_with_gemini(topics):
    """Use Gemini AI to pick best topic for viral Shorts"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        topics_text = "\n".join([f"{i+1}. {topic}" for i, topic in enumerate(topics[:20])])
        
        prompt = f"""
You are a viral YouTube Shorts expert for Indian audience.

Here are today's trending topics in India:
{topics_text}

Your task:
1. Pick the BEST topic that can get 1 crore+ views on YouTube Shorts
2. The content should be in Hinglish (Hindi + English mix)
3. Consider: shock value, curiosity, emotional connect, shareability
4. Avoid: politics, religion, controversial people

Return ONLY a JSON object like this:
{{
    "selected_topic": "the exact topic",
    "reason": "why this will go viral in 1 sentence",
    "hook": "first 3 seconds script in Hinglish",
    "title": "YouTube Short title in Hinglish (max 60 chars)",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}

Return only JSON, no other text.
"""
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean JSON
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(text)
        print(f"Selected topic: {result['selected_topic']}")
        print(f"Reason: {result['reason']}")
        return result
        
    except Exception as e:
        print(f"Gemini scoring error: {e}")
        return None

def find_best_topic():
    """Main function to find best trending topic"""
    print("=" * 50)
    print("Finding trending topics...")
    print("=" * 50)
    
    all_topics = []
    
    # Collect from all sources
    google_topics = get_google_trends()
    all_topics.extend(google_topics)
    
    news_topics = get_news_topics()
    all_topics.extend(news_topics)
    
    youtube_topics = get_youtube_trends()
    all_topics.extend(youtube_topics)
    
    if not all_topics:
        print("No topics found, using fallback")
        all_topics = [
            "India news today",
            "viral india 2025",
            "shocking facts india"
        ]
    
    print(f"Total topics collected: {len(all_topics)}")
    
    # Score with Gemini
    best_topic = score_topic_with_gemini(all_topics)
    
    if best_topic:
        # Save to file
        with open("topic.json", "w", encoding="utf-8") as f:
            json.dump(best_topic, f, ensure_ascii=False, indent=2)
        print("Topic saved to topic.json")
        return best_topic
    
    return None

if __name__ == "__main__":
    result = find_best_topic()
    if result:
        print(f"\nBest Topic: {result['selected_topic']}")
