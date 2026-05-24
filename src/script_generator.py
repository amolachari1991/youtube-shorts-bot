import requests
import os
import json

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

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
            "temperature": 0.8,
            "max_tokens": 2000
        }
        response = requests.post(
            url, headers=headers, json=data, timeout=30
        )
        result = response.json()
        if "error" in result:
            code = str(result["error"].get("code", ""))
            if "429" in code:
                return None, "QUOTA_EXHAUSTED"
            return None, f"ERROR: {result['error'].get('message', '')}"
        print("Groq responded successfully")
        return result["choices"][0]["message"]["content"], None
    except Exception as e:
        return None, f"ERROR: {str(e)}"

def call_ai(prompt):
    print("Trying Gemini...")
    text, error = call_gemini(prompt)
    if text:
        return text, None
    print(f"Gemini failed: {error}, trying Groq...")
    text, error = call_groq(prompt)
    if text:
        return text, None
    return None, f"❌ Both APIs failed: {error}"

def generate_script_and_prompts(topic_data):
    try:
        topic = topic_data.get("selected_topic", "")
        hook = topic_data.get("hook", "")
        veo_style = topic_data.get("veo_style", "cinematic documentary")

        prompt = f"""You are a viral YouTube Shorts expert for Indian audience.

Topic: {topic}
Hook: {hook}
Video Style: {veo_style}

Task 1 - Write a 15-20 second Hinglish script:
- Start with the hook
- Simple conversational Hinglish
- Shocking facts with pauses
- End with: "Follow karo aur share karo!"
- Total 60-80 words only

Task 2 - Write 2 Veo 3.1 video prompts:
- Each prompt generates 8-10 seconds of video
- Together they make 15-20 seconds total
- Style: {veo_style}
- Must be visually stunning and relevant to topic
- Include: lighting, camera angle, mood, setting
- Format for portrait 9:16 vertical video
- No text or words in video
- No people's faces (avoid copyright issues)
- Focus on: nature, cities, objects, animals, space, technology

Return ONLY this JSON, no markdown, no extra text:
{{
    "full_script": "complete hinglish script with [PAUSE] markers",
    "hook_text": "first 3 seconds text overlay for screen",
    "thumbnail_text": "5 shocking words for thumbnail",
    "description": "80 word YouTube description with hashtags",
    "veo_prompts": [
        "Detailed Veo 3.1 prompt for clip 1 (8-10 seconds)",
        "Detailed Veo 3.1 prompt for clip 2 (8-10 seconds)"
    ]
}}"""

        text, error = call_ai(prompt)
        if error:
            return None, error

        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        result = json.loads(text)
        print(f"Script generated successfully")
        print(f"Hook: {result.get('hook_text', '')}")
        print(f"Veo prompts: {len(result.get('veo_prompts', []))}")
        return result, None

    except Exception as e:
        return None, f"❌ Script generation failed: {str(e)}"

def generate_full_content():
    print("=" * 50)
    print("Generating script and Veo prompts...")
    print("=" * 50)

    try:
        with open("topic.json", "r", encoding="utf-8") as f:
            topic_data = json.load(f)
    except Exception as e:
        return None, f"❌ Could not load topic: {str(e)}"

    script, error = generate_script_and_prompts(topic_data)

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
        print(f"\nScript ready!")
        print(f"Veo prompts: {result.get('veo_prompts', [])}")
    else:
        print(f"\nFailed: {error}")
