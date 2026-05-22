import asyncio
import edge_tts
import os
import json
import re

# Best Indian male voice for Hinglish
VOICE = "hi-IN-MadhurNeural"

def clean_script(script):
    """Remove markers and clean script for voiceover"""
    # Remove [PAUSE] markers
    cleaned = script.replace("[PAUSE]", "...")
    
    # Remove extra spaces
    cleaned = " ".join(cleaned.split())
    
    return cleaned

async def generate_voice(script_text, output_file="voiceover.mp3"):
    """Generate natural Hindi voiceover using Edge TTS"""
    try:
        print(f"Generating voiceover...")
        print(f"Voice: {VOICE}")
        
        # Clean the script
        cleaned_script = clean_script(script_text)
        print(f"Script length: {len(cleaned_script)} characters")
        
        # Generate voice
        communicate = edge_tts.Communicate(
            cleaned_script,
            VOICE,
            rate="+10%",    # Slightly faster = more energetic
            volume="+0%",
            pitch="+0Hz"
        )
        
        await communicate.save(output_file)
        
        # Check file was created
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"Voiceover generated: {output_file} ({size} bytes)")
            return True
        else:
            print("Voiceover file not created")
            return False
            
    except Exception as e:
        print(f"Voice generation error: {e}")
        return False

async def generate_subtitle_timings(script_text):
    """Generate word timings for subtitles"""
    try:
        cleaned_script = clean_script(script_text)
        
        communicate = edge_tts.Communicate(
            cleaned_script,
            VOICE,
            rate="+10%"
        )
        
        timings = []
        async for chunk in communicate.stream():
            if chunk["type"] == "WordBoundary":
                timings.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10000000,  # Convert to seconds
                    "duration": chunk["duration"] / 10000000
                })
        
        print(f"Generated {len(timings)} word timings")
        return timings
        
    except Exception as e:
        print(f"Subtitle timing error: {e}")
        return []

def generate_voiceover():
    """Main function to generate voiceover from script"""
    print("=" * 50)
    print("Generating voiceover...")
    print("=" * 50)
    
    # Load script
    try:
        with open("script.json", "r", encoding="utf-8") as f:
            script_data = json.load(f)
    except Exception as e:
        print(f"Error loading script: {e}")
        return False
    
    script_text = script_data.get("full_script", "")
    
    if not script_text:
        print("No script found")
        return False
    
    print(f"Script loaded: {script_text[:100]}...")
    
    # Generate voiceover
    success = asyncio.run(generate_voice(script_text, "voiceover.mp3"))
    
    if success:
        # Generate subtitle timings
        print("Generating subtitle timings...")
        timings = asyncio.run(generate_subtitle_timings(script_text))
        
        if timings:
            with open("timings.json", "w", encoding="utf-8") as f:
                json.dump(timings, f, ensure_ascii=False, indent=2)
            print("Timings saved to timings.json")
        
        print("Voiceover generation complete!")
        return True
    
    return False

if __name__ == "__main__":
    result = generate_voiceover()
    if result:
        print("\nVoiceover ready: voiceover.mp3")
    else:
        print("\nVoiceover generation failed")
