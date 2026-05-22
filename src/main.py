import os
import json
import sys
import traceback
from trend_finder import find_best_topic
from script_generator import generate_full_content
from voice_generator import generate_voiceover
from video_maker import make_video
from notifier import notify_start, notify_video_ready, notify_error

def cleanup_old_files():
    """Remove files from previous run"""
    files_to_remove = [
        "topic.json",
        "script.json",
        "voiceover.mp3",
        "timings.json",
        "output_video.mp4",
        "temp_audio.m4a"
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed: {file}")
    
    # Clean clips folder
    if os.path.exists("clips"):
        for clip in os.listdir("clips"):
            os.remove(f"clips/{clip}")
        print("Clips folder cleaned")

def verify_api_keys():
    """Check all API keys are present"""
    required_keys = [
        "GEMINI_API_KEY",
        "PEXELS_API_KEY", 
        "NEWS_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID"
    ]
    
    missing = []
    for key in required_keys:
        if not os.environ.get(key):
            missing.append(key)
    
    if missing:
        print(f"Missing API keys: {missing}")
        return False
    
    print("All API keys verified")
    return True

def run_pipeline():
    """Run complete YouTube Shorts pipeline"""
    print("=" * 60)
    print("YOUTUBE SHORTS AUTO PIPELINE")
    print("=" * 60)
    
    # Step 0 — Verify keys
    print("\nStep 0: Verifying API keys...")
    if not verify_api_keys():
        notify_error("Missing API keys")
        sys.exit(1)
    
    # Step 1 — Notify start
    print("\nStep 1: Sending start notification...")
    notify_start()
    
    # Step 2 — Cleanup
    print("\nStep 2: Cleaning up old files...")
    cleanup_old_files()
    
    # Step 3 — Find trending topic
    print("\nStep 3: Finding trending topic...")
    topic_data = find_best_topic()
    
    if not topic_data:
        error = "Could not find trending topic"
        print(f"Error: {error}")
        notify_error(error)
        sys.exit(1)
    
    print(f"Topic found: {topic_data['selected_topic']}")
    
    # Step 4 — Generate script
    print("\nStep 4: Generating script...")
    script_data = generate_full_content()
    
    if not script_data:
        error = "Could not generate script"
        print(f"Error: {error}")
        notify_error(error)
        sys.exit(1)
    
    print("Script generated successfully")
    
    # Step 5 — Generate voiceover
    print("\nStep 5: Generating voiceover...")
    voice_success = generate_voiceover()
    
    if not voice_success:
        error = "Could not generate voiceover"
        print(f"Error: {error}")
        notify_error(error)
        sys.exit(1)
    
    print("Voiceover generated successfully")
    
    # Step 6 — Create video
    print("\nStep 6: Creating video...")
    video_success = make_video()
    
    if not video_success:
        error = "Could not create video"
        print(f"Error: {error}")
        notify_error(error)
        sys.exit(1)
    
    print("Video created successfully")
    
    # Step 7 — Send notification
    print("\nStep 7: Sending notification...")
    notify_video_ready(script_data)
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"Topic: {script_data['selected_topic']}")
    print(f"Title: {script_data['title']}")
    print("Video sent to your Telegram!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Pipeline failed: {error_msg}")
        notify_error(str(e))
        sys.exit(1)
