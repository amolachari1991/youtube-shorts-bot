import requests
import os
import json

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        })
        print("Telegram message sent")
    except Exception as e:
        print(f"Telegram error: {e}")

def send_video(path, caption):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
        with open(path, "rb") as f:
            requests.post(url, data={
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML"
            }, files={"video": f}, timeout=120)
        print("Video sent to Telegram")
    except Exception as e:
        print(f"Telegram video error: {e}")

def notify_start():
    send_message("🔄 <b>Pipeline Started</b>\n\nFinding trending topic...\nVideo ready in 15 minutes.")

def notify_error(error):
    send_message(f"⚠️ <b>Pipeline Error</b>\n\n{error}")

def notify_ready(data):
    topic = data.get("selected_topic", "")
    title = data.get("title", "")
    reason = data.get("reason", "")
    thumbnail = data.get("thumbnail_text", "")
    description = data.get("description", "")
    tags = " ".join([f"#{t}" for t in data.get("tags", [])])

    msg = f"""🎬 <b>Your Short is Ready!</b>

📌 <b>Topic:</b> {topic}

🎯 <b>Title:</b>
{title}

💡 <b>Why Viral:</b>
{reason}

🖼 <b>Thumbnail Text:</b>
{thumbnail}

📝 <b>Description:</b>
{description}

🏷 <b>Tags:</b>
{tags}

⏰ <b>Upload Times:</b>
• 7:00 AM IST
• 8:00 PM IST

✅ <b>CapCut Checklist:</b>
1. Import video
2. Add auto captions
3. Add trending sound
4. Make first frame catchy
5. Export and upload"""

    send_message(msg)

    if os.path.exists("output_video.mp4"):
        send_video("output_video.mp4", f"🎬 {title}\n\nEdit in CapCut → Upload to YouTube")
