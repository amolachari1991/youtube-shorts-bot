import requests
import os
import json
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

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
            "model": "llama3-70b-8192",
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
    """Try Gemini first, fallback to Groq"""

    print("Trying Gemini...")
    text, error = call_gemini(prompt)
    if text:
        return text, None

    if error == "QUOTA_EXHAUSTED":
        print("Gemini quota exhausted, switching to Groq...")
    elif error == "INVALID_KEY":
        return None, "❌ Gemini API key invalid\n\n✅ Fix: Update GEMINI_API_KEY in GitHub Secrets"
    else:
        print(f"Gemini error: {error}, trying Groq...")

    print("Trying Groq...")
    text, error = call_groq(prompt)
    if text:
        return text, None

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
        return None, "❌ Groq API key invalid\n\n✅ Fix: Update GROQ_API_KEY in GitHub Secrets"

    else:
        return None, f"❌ Both APIs failed\n\nReason: {error}"

def generate_script(topic_data):
    try:
        topic = topic_data.get("selected_topic", "")
        hook = topic_data.get("hook", "")

        prompt = f"""You are a viral YouTube Shorts scriptwriter for Indian audience.

Topic: {topic}
Opening Hook: {hook}

Write a 55-60 second YouTube Shorts script in Hinglish.

Rules:
1. Start with the hook provided
2. Simple conversational language
3. One fact every 5-7 seconds
4. Build curiosity throughout
5. End with: Follow karo aisi aur shocking videos ke liye
6. Total 130-150 words only
7. Write as someone would SPEAK
8. Add [PAUSE] for dramatic effect

Return ONLY this JSON, no other text:
{{
    "full_script": "complete script with [PAUSE] markers",
    "hook_text": "first 3 seconds text for screen",
    "key_points": ["point1", "point2", "point3"],
    "thumbnail_text": "max 5 bold words for thumbnail",
    "description": "100 word YouTube description with hashtags"
}}"""

        text, error = call_ai(prompt)

        if error:
            return None, error

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)
        print(f"Script generated")
        print(f"Hook: {result['hook_text']}")
        return result, None

    except Exception as e:
        return None, f"❌ Script generation failed\n\nReason: {str(e)}"

def generate_full_content():
    print("=" * 50)
    print("Generating script...")
    print("=" * 50)

    try:
        with open("topic.json", "r", encoding="utf-8") as f:
            topic_data = json.load(f)
    except Exception as e:
        return None, f"❌ Could not load topic\n\nReason: {str(e)}"

    script, error = generate_script(topic_data)

    if error:
        return None, error

    if script:
        full = {**topic_data, **script}
        with open("script.json", "w", encoding="utf-8") as f:
            json.dump(full, f, ensure_ascii=False, indent=2)
        print("Saved script.json")
        return full, None

    return None, "❌ Unknown script error"

if __name__ == "__main__":
    result, error = generate_full_content()
    if result:
        print(f"Script ready for: {result['selected_topic']}")
    else:
        print(f"Failed: {error}")
