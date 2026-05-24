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

def send_audio(path, caption):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAudio"
        with open(path, "rb") as f:
            requests.post(url, data={
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption
            }, files={"audio": f}, timeout=60)
        print("Audio sent to Telegram")
    except Exception as e:
        print(f"Audio send error: {e}")

def notify_start():
    send_message("🔄 <b>Pipeline Started</b>\n\nFinding today's trending topic...\nReady in 10 minutes.")

def notify_error(error):
    send_message(f"⚠️ <b>Pipeline Error</b>\n\n{error}")

def notify_ready(data):
    topic = data.get("selected_topic", "")
    title = data.get("title", "")
    reason = data.get("reason", "")
    hook = data.get("hook", "")
    thumbnail = data.get("thumbnail_text", "")
    description = data.get("description", "")
    tags = " ".join([f"#{t}" for t in data.get("tags", [])])
    veo_prompts = data.get("veo_prompts", [])
    script = data.get("full_script", "")
    veo_style = data.get("veo_style", "cinematic documentary")

    # Message 1 - Topic and Script
    msg1 = f"""🎬 <b>Today's Short is Ready!</b>

📌 <b>Topic:</b> {topic}

🎯 <b>YouTube Title:</b>
{title}

💡 <b>Why Viral:</b> {reason}

🎤 <b>Hook (First 3 seconds):</b>
{hook}

📝 <b>Full Script:</b>
{script}

🖼 <b>Thumbnail Text:</b>
{thumbnail}

📋 <b>Description:</b>
{description}

🏷 <b>Tags:</b>
{tags}"""

    send_message(msg1)

    # Message 2 - Veo 3.1 Prompts
    if veo_prompts:
        prompts_text = ""
        for i, prompt in enumerate(veo_prompts):
            prompts_text += f"\n\n🎬 <b>Clip {i+1}:</b>\n{prompt}"

        msg2 = f"""🎨 <b>Gemini Veo 3.1 Prompts</b>
Style: {veo_style}

Copy each prompt into Gemini app → Videos tab:
{prompts_text}

⚡ <b>Steps:</b>
1. Open Gemini app
2. Tap Videos
3. Paste Clip 1 prompt → Generate
4. After generation tap Extend
5. Paste Clip 2 prompt → Generate
6. Repeat for all clips
7. Download all clips
8. Assemble in VN editor
9. Add voiceover (attached below)
10. Upload to YouTube"""

        send_message(msg2)

    # Message 3 - Upload Times
    msg3 = f"""⏰ <b>Best Upload Times:</b>
• Morning → 7:00 AM IST
• Evening → 8:00 PM IST

✅ <b>VN Editor Checklist:</b>
1. Import all Veo clips in order
2. Add voiceover audio (attached)
3. Add auto captions
4. Add background music (low volume)
5. Export 1080p 30fps
6. Upload with title and tags above

🚀 Consistency = Monetization!"""

    send_message(msg3)

    # Send voiceover audio
    if os.path.exists("voiceover.mp3"):
        send_audio(
            "voiceover.mp3",
            f"🎤 Voiceover for: {title}\n\nUse this in VN editor"
        )
