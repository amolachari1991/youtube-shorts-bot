import os
import json
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

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
        print(f"Script generated")
        print(f"Hook: {result['hook_text']}")
        return result

    except Exception as e:
        print(f"Script error: {e}")
        return None

def generate_full_content():
    print("=" * 50)
    print("Generating script...")
    print("=" * 50)

    try:
        with open("topic.json", "r", encoding="utf-8") as f:
            topic_data = json.load(f)
    except Exception as e:
        print(f"Error loading topic: {e}")
        return None

    script = generate_script(topic_data)

    if script:
        full = {**topic_data, **script}
        with open("script.json", "w", encoding="utf-8") as f:
            json.dump(full, f, ensure_ascii=False, indent=2)
        print("Saved script.json")
        return full

    return None

if __name__ == "__main__":
    result = generate_full_content()
    if result:
        print(f"Script ready for: {result['selected_topic']}")
