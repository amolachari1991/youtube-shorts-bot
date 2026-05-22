import os
import json
import sys
import traceback

from trend_finder import find_best_topic
from script_generator import generate_full_content
from voice_generator import generate_voiceover
from video_maker import make_video
from notifier import notify_start, notify_ready, notify_error

def cleanup():
    files = [
        "topic.json",
        "script.json",
        "voiceover.mp3",
        "timings.json",
        "output_video.mp4",
        "temp_audio.m4a"
    ]
    for f in files:
        if os.path.exists(f):
            os.remove(f)
            print(f"Removed: {f}")

    if os.path.exists("clips"):
        for c in os.listdir("clips"):
            try:
                os.remove(f"clips/{c}")
            except:
                pass
        print("Clips cleaned")

def check_keys():
    keys = [
        "GEMINI_API_KEY",
        "PEXELS_API_KEY",
        "NEWS_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID"
    ]
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        print(f"Missing keys: {missing}")
        return False
    print("All keys verified")
    return True

def run():
    print("=" * 60)
    print("YOUTUBE SHORTS AUTO PIPELINE")
    print("=" * 60)

    # Check keys
    print("\nChecking API keys...")
    if not check_keys():
        notify_error("Missing API keys")
        sys.exit(1)

    # Notify start
    print("\nSending start notification...")
    notify_start()

    # Cleanup
    print("\nCleaning old files...")
    cleanup()

    # Step 1 - Find topic
    print("\nStep 1: Finding trending topic...")
    topic = find_best_topic()
    if not topic:
        notify_error("Could not find trending topic")
        sys.exit(1)
    print(f"Topic: {topic['selected_topic']}")

    # Step 2 - Generate script
    print("\nStep 2: Generating script...")
    script = generate_full_content()
    if not script:
        notify_error("Could not generate script")
        sys.exit(1)
    print("Script ready")

    # Step 3 - Generate voice
    print("\nStep 3: Generating voiceover...")
    voice = generate_voiceover()
    if not voice:
        notify_error("Could not generate voiceover")
        sys.exit(1)
    print("Voiceover ready")

    # Step 4 - Make video
    print("\nStep 4: Creating video...")
    video = make_video()
    if not video:
        notify_error("Could not create video")
        sys.exit(1)
    print("Video ready")

    # Step 5 - Notify done
    print("\nStep 5: Sending notification...")
    notify_ready(script)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE!")
    print(f"Topic: {script['selected_topic']}")
    print(f"Title: {script['title']}")
    print("Video sent to Telegram!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Pipeline failed: {msg}")
        notify_error(str(e))
        sys.exit(1)
