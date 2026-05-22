import asyncio
import edge_tts
import os
import json

VOICE = "hi-IN-MadhurNeural"

def clean_script(text):
    cleaned = text.replace("[PAUSE]", "...")
    cleaned = " ".join(cleaned.split())
    return cleaned

async def create_voice(text, output="voiceover.mp3"):
    try:
        print(f"Generating voice...")
        cleaned = clean_script(text)
        print(f"Script length: {len(cleaned)} chars")

        communicate = edge_tts.Communicate(
            cleaned,
            VOICE,
            rate="+10%",
            volume="+0%",
            pitch="+0Hz"
        )

        await communicate.save(output)

        if os.path.exists(output):
            size = os.path.getsize(output)
            print(f"Voice saved: {output} ({size} bytes)")
            return True
        return False

    except Exception as e:
        print(f"Voice error: {e}")
        return False

def generate_voiceover():
    print("=" * 50)
    print("Generating voiceover...")
    print("=" * 50)

    try:
        with open("script.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading script: {e}")
        return False

    script = data.get("full_script", "")

    if not script:
        print("No script found")
        return False

    print(f"Script: {script[:80]}...")
    success = asyncio.run(create_voice(script, "voiceover.mp3"))

    if success:
        print("Voiceover complete!")
    return success

if __name__ == "__main__":
    result = generate_voiceover()
    if result:
        print("voiceover.mp3 ready")
    else:
        print("Voiceover failed")
