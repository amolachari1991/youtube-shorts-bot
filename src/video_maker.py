import requests
import os
import json
import random
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip
)

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")
WIDTH = 1080
HEIGHT = 1920

def download_clips(topic, num=5):
    try:
        print(f"Searching videos for: {topic}")
        words = " ".join(str(topic).split()[:3])
        headers = {"Authorization": PEXELS_API_KEY}
        url = "https://api.pexels.com/videos/search"
        params = {
            "query": words,
            "per_page": num,
            "orientation": "portrait"
        }
        response = requests.get(
            url, headers=headers, params=params, timeout=15
        )
        data = response.json()
        videos = data.get("videos", [])

        if len(videos) < 2:
            params["query"] = "india city people"
            response = requests.get(
                url, headers=headers, params=params, timeout=15
            )
            data = response.json()
            videos = data.get("videos", [])

        os.makedirs("clips", exist_ok=True)
        downloaded = []

        for i, video in enumerate(videos[:num]):
            try:
                files = video.get("video_files", [])
                if not files:
                    continue
                files_sorted = sorted(
                    files, key=lambda x: x.get("width", 0)
                )
                picked = files_sorted[len(files_sorted) // 2]
                link = picked.get("link", "")
                if not link:
                    continue
                print(f"Downloading clip {i+1}...")
                r = requests.get(link, stream=True, timeout=30)
                path = f"clips/clip_{i+1}.mp4"
                with open(path, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)
                downloaded.append(path)
                print(f"Clip {i+1} saved")
            except Exception as e:
                print(f"Clip {i+1} error: {e}")
                continue

        print(f"Downloaded {len(downloaded)} clips")
        return downloaded

    except Exception as e:
        print(f"Pexels error: {e}")
        return []

def process_clip(path, duration=10):
    try:
        clip = VideoFileClip(path)

        # Trim clip
        if clip.duration > duration:
            start = random.uniform(0, clip.duration - duration)
            clip = clip.with_subclip(start, start + duration)

        # Crop to portrait
        clip_ratio = clip.w / clip.h
        target_ratio = WIDTH / HEIGHT

        if clip_ratio > target_ratio:
            new_w = int(clip.h * target_ratio)
            x = clip.w // 2
            clip = clip.cropped(
                x1=x - new_w // 2,
                x2=x + new_w // 2
            )
        else:
            new_h = int(clip.w / target_ratio)
            y = clip.h // 2
            clip = clip.cropped(
                y1=y - new_h // 2,
                y2=y + new_h // 2
            )

        clip = clip.resized((WIDTH, HEIGHT))
        return clip

    except Exception as e:
        print(f"Process clip error: {e}")
        return None

def assemble_video(script_data, clips, output="output_video.mp4"):
    try:
        print("Assembling video...")
        audio = AudioFileClip("voiceover.mp3")
        duration = audio.duration
        print(f"Audio duration: {duration:.1f}s")

        clip_dur = max(duration / max(len(clips), 1), 3)

        processed = []
        for path in clips:
            c = process_clip(path, clip_dur)
            if c:
                processed.append(c)

        if not processed:
            print("Using black background")
            bg = ColorClip(
                size=(WIDTH, HEIGHT),
                color=[0, 0, 0],
                duration=duration
            )
            processed = [bg]

        if len(processed) > 1:
            video = concatenate_videoclips(
                processed, method="compose"
            )
        else:
            video = processed[0]

        if video.duration < duration:
            loops = int(duration / video.duration) + 1
            video = concatenate_videoclips(
                [video] * loops, method="compose"
            )

        video = video.with_subclip(0, duration)

        overlay = ColorClip(
            size=(WIDTH, HEIGHT),
            color=[0, 0, 0],
            duration=duration
        ).with_opacity(0.3)

        layers = [video, overlay]

        hook = script_data.get("hook_text", "")
        if hook:
            try:
                hook_clip = TextClip(
                    text=hook,
                    font_size=70,
                    color="yellow",
                    font="DejaVu-Sans-Bold",
                    method="caption",
                    size=(WIDTH - 100, None),
                    text_align="center",
                    duration=4
                ).with_position("center")
                layers.append(hook_clip.with_start(0))
            except Exception as e:
                print(f"Hook text error: {e}")

        try:
            watermark = TextClip(
                text="FOLLOW FOR MORE",
                font_size=35,
                color="white",
                font="DejaVu-Sans-Bold",
                duration=duration
            ).with_position(("center", HEIGHT - 150))
            layers.append(watermark)
        except Exception as e:
            print(f"Watermark error: {e}")

        final = CompositeVideoClip(layers)
        final = final.with_subclip(0, duration)
        final = final.with_audio(audio)

        print(f"Exporting to {output}...")
        final.write_videofile(
            output,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp_audio.m4a",
            remove_temp=True,
            verbose=False,
            logger=None
        )
        print(f"Video exported: {output}")
        return True

    except Exception as e:
        print(f"Assembly error: {e}")
        return False

def make_video():
    print("=" * 50)
    print("Creating YouTube Short...")
    print("=" * 50)

    try:
        with open("script.json", "r", encoding="utf-8") as f:
            script_data = json.load(f)
    except Exception as e:
        print(f"Error loading script: {e}")
        return False

    topic = script_data.get("selected_topic", "india trending")
    print(f"Topic: {topic}")

    clips = download_clips(topic, num=6)
    if not clips:
        print("No clips downloaded")
        return False

    success = assemble_video(script_data, clips, "output_video.mp4")
    if success:
        print("Video ready!")
        return True

    return False

if __name__ == "__main__":
    result = make_video()
    if result:
        print("output_video.mp4 ready!")
    else:
        print("Video creation failed")
