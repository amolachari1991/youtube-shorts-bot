import requests
import os
import json

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    """Send text message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Telegram message sent successfully")
            return True
        else:
            print(f"Telegram error: {response.text}")
            return False
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def send_telegram_video(video_path, caption):
    """Send video file to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        
        print(f"Sending video to Telegram: {video_path}")
        
        with open(video_path, "rb") as video_file:
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML"
            }
            files = {
                "video": video_file
            }
            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=120
            )
        
        if response.status_code == 200:
            print("Video sent to Telegram successfully")
            return True
        else:
            print(f"Telegram video error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Telegram video send error: {e}")
        return False

def notify_video_ready(script_data):
    """Send complete notification when video is ready"""
    try:
        topic = script_data.get("selected_topic", "Unknown")
        title = script_data.get("title", "Unknown")
        reason = script_data.get("reason", "")
        thumbnail_text = script_data.get("thumbnail_text", "")
        description = script_data.get("description", "")
        tags = script_data.get("tags", [])
        
        # Format tags
        tags_text = " ".join([f"#{tag}" for tag in tags])
        
        # Create message
        message = f"""
🎬 <b>Your YouTube Short is Ready!</b>

📌 <b>Topic:</b> {topic}

🎯 <b>YouTube Title:</b>
{title}

💡 <b>Why This Will Viral:</b>
{reason}

🖼 <b>Thumbnail Text:</b>
{thumbnail_text}

📝 <b>Description to Copy:</b>
{description}

🏷 <b>Tags:</b>
{tags_text}

⏰ <b>Best Upload Times:</b>
• Morning Short → 7:00 AM IST
• Evening Short → 8:00 PM IST

✅ <b>Your CapCut Checklist:</b>
1. Import video
2. Add auto captions
3. Add trending sound
4. Make first frame eye-catching
5. Export and upload

🚀 <b>Consistency = Monetization!</b>
"""
        
        # Send text message first
        send_telegram_message(message)
        
        # Send video file if exists
        if os.path.exists("output_video.mp4"):
            caption = f"🎬 {title}\n\nDownload → Edit in CapCut → Upload to YouTube"
            send_telegram_video("output_video.mp4", caption)
        
        return True
        
    except Exception as e:
        print(f"Notification error: {e}")
        return False

def notify_error(error_message):
    """Send error notification"""
    message = f"""
⚠️ <b>Pipeline Error</b>

Error: {error_message}

Pipeline will retry in next scheduled run.
"""
    send_telegram_message(message)

def notify_start():
    """Send start notification"""
    message = """
🔄 <b>Pipeline Started</b>

Finding today's trending topic...
Video will be ready in 10-15 minutes.
"""
    send_telegram_message(message)

if __name__ == "__main__":
    # Test notification
    send_telegram_message("✅ Telegram notifications working!")
