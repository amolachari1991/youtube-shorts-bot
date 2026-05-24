import requests
import os
import json
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

def call_gemini(prompt):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        print("Gemini responded successfully")
        return response.text.strip(), None
    except Exception as e:
        error = str(e)
        if "429" in error or "RESOURCE_EXHAUSTED" in error:
            return None, "QUOTA_EXHAUSTED"
        elif "401" in error or "403" in error:
            return None, "INVALID_KEY"
        else:
            return None, f"ERROR: {error}"

def call_groq(prompt):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        response = requests.post(
            url, headers=headers, json=data, timeout=30
        )
        result = response.json()

        if "error" in result:
            error = result["error"].get("message", "")
            if "429" in str(result["error"].get("code", "")):
                return None, "QUOTA_EXHAUSTED"
            elif "401" in str(result["error"].get("code", "")):
                return None, "INVALID_KEY"
            else:
                return None, f"ERROR: {error}"

        print("Groq responded successfully")
        return result["choices"][0]["message"]["content"], None

    except Exception as e:
        return None, f"ERROR: {str(e)}"

def call_ai(prompt):
    """Try Gemini first, fallback to Groq with smart error handling"""

    # Try Gemini
    print("Trying Gemini...")
    text, error = call_gemini(prompt)
    if text:
        return text, None

    # Handle Gemini failure
    if error == "QUOTA_EXHAUSTED":
        print("Gemini quota exhausted, switching to Groq...")
    elif error == "INVALID_KEY":
        return None, "❌ Gemini API key is invalid\n\n✅ Fix: Update GEMINI_API_KEY in GitHub Secrets"
    else:
        print(f"Gemini error: {error}, trying Groq...")

    # Try Groq
    print("Trying Groq...")
    text, error = call_groq(prompt)
    if text:
        return text, None

    # Handle Groq failure
    if error == "QUOTA_EXHAUSTED":
        return None, """❌ Both Gemini and Groq quota exhausted

✅ What to do:
1. Wait until tomorrow for quota reset
   OR
2. Create new Gemini key:
   • Go to aistudio.google.com
   • Create new API key
   • Update GEMINI_API_KEY in GitHub Secrets"""

    elif error == "INVALID_KEY":
        return None, "❌ Groq API key is invalid\n\n✅ Fix: Update GROQ_API_KEY in GitHub Secrets"

    else:
        return None, f"❌ Both AI APIs failed\n\nReason: {error}\n\n✅ Fix: Check your internet or API keys"

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

    text, error = call_ai(prompt)

    if error:
        return None, error

    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)
        print(f"Topic: {result['selected_topic']}")
        return result, None

    except Exception as e:
        return None, f"❌ AI response parsing failed\n\nReason: {str(e)}"

def find_best_topic():
    print("=" * 50)
    print("Finding trending topics...")
    print("=" * 50)

    all_topics = []
    all_topics.extend(get_news_topics())
    all_topics.extend(get_extra_topics())

    if not all_topics:
        print("No news found, using fallback topics")
        all_topics = [
            "India shocking news today",
            "viral india 2025",
            "unbelievable india facts",
            "india trending today",
            "shocking facts hindi"
        ]

    print(f"Total topics: {len(all_topics)}")
    result, error = score_topic(all_topics)

    if error:
        print(f"Pipeline error: {error}")
        return None, error

    if result:
        with open("topic.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("Saved topic.json")
        return result, None

    return None, "❌ Unknown error finding topic"

if __name__ == "__main__":
    result, error = find_best_topic()
    if result:
        print(f"Best Topic: {result['selected_topic']}")
    else:
        print(f"Failed: {error}")
