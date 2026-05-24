import requests
import os
import json
import datetime
import random

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY")

def call_gemini(prompt):
    try:
        from google import genai
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
            "temperature": 0.9,
            "max_tokens": 1000
        }
        response = requests.post(
            url, headers=headers, json=data, timeout=30
        )
        result = response.json()
        if "error" in result:
            code = str(result["error"].get("code", ""))
            msg = result["error"].get("message", "")
            if "429" in code:
                return None, "QUOTA_EXHAUSTED"
            elif "401" in code:
                return None, "INVALID_KEY"
            else:
                return None, f"ERROR: {msg}"
        print("Groq responded successfully")
        return result["choices"][0]["message"]["content"], None
    except Exception as e:
        return None, f"ERROR: {str(e)}"

def call_ai(prompt):
    print("Trying Gemini...")
    text, error = call_gemini(prompt)
    if text:
        return text, None
    if error == "QUOTA_EXHAUSTED":
        print("Gemini exhausted, switching to Groq...")
    else:
        print(f"Gemini error: {error}, trying Groq...")
    print("Trying Groq...")
    text, error = call_groq(prompt)
    if text:
        return text, None
    if error == "QUOTA_EXHAUSTED":
        return None, "❌ Both Gemini and Groq quota exhausted\n\nWait until tomorrow or add new API key"
    elif error == "INVALID_KEY":
        return None, "❌ API key invalid\n\nCheck your API keys in GitHub Secrets"
    else:
        return None, f"❌ Both APIs failed\n\nReason: {error}"

def get_gnews_headlines():
    try:
        url = "https://gnews.io/api/v4/top-headlines"
        params = {
            "country": "in",
            "lang": "en",
            "max": 20,
            "apikey": GNEWS_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        topics = []
        if data.get("articles"):
            for article in data["articles"]:
                if article.get("title"):
                    topics.append(article["title"])
                if article.get("description"):
                    topics.append(article["description"])
        print(f"GNews headlines: {len(topics)}")
        return topics
    except Exception as e:
        print(f"GNews headlines error: {e}")
        return []

def get_gnews_viral():
    try:
        queries = [
            "india amazing facts",
            "india shocking discovery",
            "india science technology",
            "india world record",
            "india viral trending"
        ]
        # Pick different queries each day
        day = datetime.datetime.now().day
        selected_queries = queries[day % len(queries):] + queries[:day % len(queries)]
        selected_queries = selected_queries[:2]

        topics = []
        for query in selected_queries:
            url = "https://gnews.io/api/v4/search"
            params = {
                "q": query,
                "lang": "en",
                "country": "in",
                "max": 10,
                "apikey": GNEWS_API_KEY,
                "sortby": "relevance"
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data.get("articles"):
                for article in data["articles"]:
                    if article.get("title"):
                        topics.append(article["title"])
                    if article.get("description"):
                        topics.append(article["description"])
        print(f"GNews viral: {len(topics)}")
        return topics
    except Exception as e:
        print(f"GNews viral error: {e}")
        return []

def get_diverse_fallback():
    """Different topics each day based on date"""
    now = datetime.datetime.now()
    day = now.day
    hour = now.hour

    all_topics = [
        # Week 1 topics
        "India discovers massive gold reserve under Bihar",
        "Indian scientist invents device that converts air to water",
        "Mumbai underground metro reveals hidden ancient city",
        "Indian village where nobody has died in 100 years",
        "ISRO finds water on Moon in historic mission",
        "Indian farmer grows vegetable worth 1 lakh per kg",
        "India builds world longest sea bridge in record time",
        # Week 2 topics
        "Indian student solves 100 year old math problem",
        "Mysterious lake in Himalayas glows blue at night",
        "India beats USA in space technology for first time",
        "Ancient Indian temple found underwater near Gujarat",
        "Indian doctor creates medicine that cures cancer",
        "Tiger population in India doubles shocking experts",
        "India creates AI that predicts earthquake 3 days early",
        # Week 3 topics
        "Indian village where everyone speaks Sanskrit only",
        "DRDO creates bulletproof jacket lighter than paper",
        "India finds oil reserve bigger than Saudi Arabia",
        "Indian child prodigy graduates college at age 10",
        "Oldest living human found in remote Indian village",
        "India launches world first hydrogen powered train",
        "Ancient map proves India knew about America before Columbus",
        # Week 4 topics
        "Indian startup creates fuel from plastic waste",
        "Mysterious radio signals detected from Indian Ocean",
        "India creates robot that performs surgery better than doctor",
        "Sunken ancient city found in Indian ocean by ISRO",
        "Indian engineer creates car engine that runs on water",
        "Lost tribe discovered in Andaman with unknown language",
        "India breaks world record for most trees planted in one day",
    ]

    # Pick based on day and hour for variety
    seed = day * 24 + hour
    random.seed(seed)
    selected = random.sample(all_topics, min(10, len(all_topics)))
    print(f"Diverse fallback topics for day {day} hour {hour}: {len(selected)}")
    return selected

def score_topic(topics):
    # Remove duplicates
    unique_topics = list(dict.fromkeys(topics))

    # Add current date/time context for AI
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %d %B %Y")

    topics_text = "\n".join(
        [f"{i+1}. {t}" for i, t in enumerate(unique_topics[:25])]
    )

    prompt = f"""You are a viral YouTube Shorts expert for Indian audience.
Today's date: {date_str}

Today's trending topics in India:
{topics_text}

Pick the BEST single topic for 1 crore+ views on YouTube Shorts.
Content must be Hinglish (Hindi + English mix).
Must be: shocking OR surprising OR emotional OR curiosity-inducing.
Avoid: politics, religion, specific politicians, violence.
Pick something DIFFERENT and FRESH - not generic.

Return ONLY this JSON, no markdown, no extra text:
{{
    "selected_topic": "specific clear topic",
    "reason": "one line why Indians will share this",
    "hook": "shocking first 3 second line in Hinglish",
    "title": "YouTube Shorts title in Hinglish max 55 chars",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "veo_style": "cinematic style for video eg: documentary, dramatic, aerial"
}}"""

    text, error = call_ai(prompt)
    if error:
        return None, error

    try:
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        result = json.loads(text)
        print(f"Selected topic: {result['selected_topic']}")
        return result, None
    except Exception as e:
        return None, f"❌ AI response parsing failed: {str(e)}\nRaw: {text[:200]}"

def find_best_topic():
    print("=" * 50)
    print("Finding trending topics...")
    print("=" * 50)

    all_topics = []

    # GNews headlines (primary source)
    headlines = get_gnews_headlines()
    all_topics.extend(headlines)

    # GNews viral search
    viral = get_gnews_viral()
    all_topics.extend(viral)

    # Always add diverse fallback for variety
    fallback = get_diverse_fallback()
    all_topics.extend(fallback)

    # Remove duplicates
    all_topics = list(dict.fromkeys(all_topics))
    print(f"Total unique topics: {len(all_topics)}")

    best, error = score_topic(all_topics)

    if error:
        print(f"Error: {error}")
        return None, error

    if best:
        with open("topic.json", "w", encoding="utf-8") as f:
            json.dump(best, f, ensure_ascii=False, indent=2)
        print(f"Saved: {best['selected_topic']}")
        return best, None

    return None, "❌ Unknown error"

if __name__ == "__main__":
    result, error = find_best_topic()
    if result:
        print(f"\nBest Topic: {result['selected_topic']}")
    else:
        print(f"\nFailed: {error}")
