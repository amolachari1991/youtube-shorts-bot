import google.generativeai as genai
import os
import json

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def generate_script(topic_data):
    """Generate Hinglish script for YouTube Short"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        topic = topic_data.get("selected_topic", "")
        hook = topic_data.get("hook", "")
        
        prompt = f"""
You are a viral YouTube Shorts scriptwriter for Indian audience.

Topic: {topic}
Opening Hook: {hook}

Write a 55-60 second YouTube Shorts script in Hinglish (Hindi + English mix).

Rules:
1. First 3 seconds = shocking hook (already provided above, use it)
2. Use simple conversational language
3. One fact or point every 5-7 seconds
4. Build curiosity throughout
5. End with "Follow karo aisi aur shocking videos ke liye"
6. Total words = 130-150 words only
7. Write naturally as someone would SPEAK, not read
8. Add [PAUSE] where speaker should pause for effect

Return ONLY a JSON object like this:
{{
    "full_script": "complete script here with [PAUSE] markers",
    "hook_text": "first 3 seconds text for screen overlay",
    "key_points": ["point 1", "point 2", "point 3"],
    "thumbnail_text": "bold text for thumbnail max 5 words",
    "description": "YouTube video description 100 words with hashtags"
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
        print(f"Script generated successfully")
        print(f"Hook text: {result['hook_text']}")
        return result
        
    except Exception as e:
        print(f"Script generation error: {e}")
        return None

def generate_full_content():
    """Load topic and generate complete script"""
    print("=" * 50)
    print("Generating script...")
    print("=" * 50)
    
    # Load topic
    try:
        with open("topic.json", "r", encoding="utf-8") as f:
            topic_data = json.load(f)
    except Exception as e:
        print(f"Error loading topic: {e}")
        return None
    
    # Generate script
    script_data = generate_script(topic_data)
    
    if script_data:
        # Merge topic and script data
        full_data = {**topic_data, **script_data}
        
        # Save to file
        with open("script.json", "w", encoding="utf-8") as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)
        
        print("Script saved to script.json")
        print(f"Thumbnail text: {script_data['thumbnail_text']}")
        return full_data
    
    return None

if __name__ == "__main__":
    result = generate_full_content()
    if result:
        print(f"\nScript ready for: {result['selected_topic']}")
        print(f"\nScript preview:")
        print(result['full_script'][:200] + "...")
