import requests
import os
import json
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

def get_news_topics():
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "in",
            "apiKey": NEWS_API_KEY,
            "pageSize": 20
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        topics = []
        if data.get("articles"):
            for article in data["articles"]:
                if article.get("title"):
                    topics.append(article["title"])
        print(f"News topics: {len(topics)}")
        return topics
    except Exception as e:
        print(f"News error: {e}")
        return []

def get_extra_topics():
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "india viral trending",
            "apiKey": NEWS_API_KEY,
            "pageSize": 10,
            "sortBy": "popularity",
            "language": "en"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        topics = []
        if data.get("articles"):
            for article in data["articles"]:
                if article.get("title"):
                    topics.append(article["title"])
        print(f"Extra topics: {len(topics)}")
        return topics
    except Exception as e:
        print(f"Extra topics error: {e}")
        return []

def score_topic(topics):
    try:
        topics_text = "\n".join(
            [f"{i+1}. {t}" for i, t in enumerate(topics[:20])]
        )

        prompt = f"""You are a viral YouTube Shorts expert for Indian audience.

Today's trending topics in India:
{topics_text}

Pick the BEST topic for 1 crore+ views on YouTube Shorts.
Content should be Hinglish (Hindi + English mix).
Avoid politics, religion, controversial people.

Return ONLY this JSON, no other text:
{{
    "selected_topic": "topic here",
    "reason": "one line why viral",
    "hook": "first 3 seconds script in Hinglish",
    "title": "YouTube title max 60 chars",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.strip()

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)
        print(f"Topic: {result['selected_topic']}")
        return result

    except Exception as e:
        print(f"Gemini error: {e}")
        return {
            "selected_topic": "India shocking facts 2025",
            "reason": "Always viral in India",
            "hook": "Ye baat 99% log nahi jaante...",
            "title": "99% Indians Don't Know This Shocking Fact",
            "tags": ["india", "facts", "viral", "shocking", "hindi"]
        }

def find_best_topic():
    print("=" * 50)
    print("Finding trending topics...")
    print("=" * 50)

    all_topics = []
    all_topics.extend(get_news_topics())
    all_topics.extend(get_extra_topics())

    if not all_topics:
        all_topics = [
            "India shocking news today",
            "viral india 2025",
            "unbelievable india facts",
            "india trending today",
            "shocking facts hindi"
        ]

    print(f"Total topics: {len(all_topics)}")
    best = score_topic(all_topics)

    if best:
        with open("topic.json", "w", encoding="utf-8") as f:
            json.dump(best, f, ensure_ascii=False, indent=2)
        print("Saved topic.json")
        return best

    return None

if __name__ == "__main__":
    result = find_best_topic()
    if result:
        print(f"Best Topic: {result['selected_topic']}")
