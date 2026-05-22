import requests
import os
import json
import random
from moviepy import (
    VideoFileClip, AudioFileClip, TextClip,
    CompositeVideoClip, concatenate_videoclips,
    ColorClip
)
import numpy as np

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY")

# YouTube Shorts dimensions
WIDTH = 1080
HEIGHT = 1920

def download_stock_videos(topic, num_videos=5):
    """Download relevant stock videos from Pexels"""
    try:
        print(f"Searching stock videos for: {topic}")
        
        # Clean topic for search
        search_query = topic.replace("#", "").strip()
        # Take first 3 words for better results
        search_words = " ".join(search_query.split()[:3])
        
        headers = {"Authorization": PEXELS_API_KEY}
        
        # Try topic specific search first
        url = "https://api.pexels.com/videos/search"
        params = {
            "query": search_words,
            "per_page": num_videos,
            "orientation": "portrait",
            "size": "medium"
        }
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        videos = data.get("videos", [])
        
        # Fallback to generic India videos if not enough
        if len(videos) < 3:
            print("Using fallback search: india trending")
            params["query"] = "india city people"
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            videos = data.get("videos", [])
        
        downloaded = []
        os.makedirs("clips", exist_ok=True)
        
        for i, video in enumerate(videos[:num_videos]):
            try:
                # Get best quality video file
                video_files = video.get("video_files", [])
                
                # Sort by quality
                portrait_files = [
                    f for f in video_files
                    if f.get("width", 0) <= 1080
                ]
                
                if not portrait_files:
                    portrait_files = video_files
                
                # Pick medium quality for faster download
                best_file = sorted(
                    portrait_files,
                    key=lambda x: x.get("width", 0)
                )[len(portrait_files)//2]
                
                video_url = best_file.get("link", "")
                
                if video_url:
                    print(f"Downloading clip {i+1}...")
                    video_response = requests.get(
                        video_url,
                        stream=True,
                        timeout=30
                    )
                    
                    clip_path = f"clips/clip_{i+1}.mp4"
                    with open(clip_path, "wb") as f:
                        for chunk in video_response.iter_content(
                            chunk_size=8192
                        ):
                            f.write(chunk)
                    
                    downloaded.append(clip_path)
                    print(f"Clip {i+1} downloaded: {clip_path}")
                    
            except Exception as e:
                print(f"Error downloading clip {i+1}: {e}")
                continue
        
        print(f"Total clips downloaded: {len(downloaded)}")
        return downloaded
        
    except Exception as e:
        print(f"Pexels error: {e}")
        return []

def create_text_clip(text, duration, fontsize=60,
                     color="white", bg_color=None,
                     position=("center", "center")):
    """Create a text overlay clip"""
    try:
        txt_clip = TextClip(
            text,
            fontsize=fontsize,
            color=color,
            font="DejaVu-Sans-Bold",
            method="caption",
            size=(WIDTH - 100, None),
            align="center"
        ).set_duration(duration)
        
        if bg_color:
            txt_clip = txt_clip.on_color(
                size=(WIDTH, txt_clip.h + 20),
                color=bg_color,
                col_opacity=0.6
            )
        
        return txt_clip.set_position(position)
        
    except Exception as e:
        print(f"Text clip error: {e}")
        return None

def process_video_clip(clip_path, target_duration=10):
    """Process a single video clip to fit Shorts format"""
    try:
        clip = VideoFileClip(clip_path)
        
        # Trim to target duration
        if clip.duration > target_duration:
            start = random.uniform(0, clip.duration - target_duration)
            clip = clip.subclip(start, start + target_duration)
        
        # Resize to portrait format (1080x1920)
        clip_ratio = clip.w / clip.h
        target_ratio = WIDTH / HEIGHT
        
        if clip_ratio > target_ratio:
            # Wider than needed - crop sides
            new_width = int(clip.h * target_ratio)
            x_center = clip.w // 2
            clip = clip.crop(
                x1=x_center - new_width//2,
                x2=x_center + new_width//2
            )
        else:
            # Taller than needed - crop top/bottom
            new_height = int(clip.w / target_ratio)
            y_center = clip.h // 2
            clip = clip.crop(
                y1=y_center - new_height//2,
                y2=y_center + new_height//2
            )
        
        # Resize to exact dimensions
        clip = clip.resize((WIDTH, HEIGHT))
        
        return clip
        
    except Exception as e:
        print(f"Error processing clip {clip_path}: {e}")
        return None

def create_shorts_video(script_data, video_clips, output_file="output_video.mp4"):
    """Assemble final YouTube Short"""
    try:
        print("Assembling video...")
        
        # Load audio
        audio = AudioFileClip("voiceover.mp3")
        total_duration = audio.duration
        print(f"Audio duration: {total_duration:.1f} seconds")
        
        # Calculate clip duration
        num_clips = len(video_clips)
        clip_duration = total_duration / max(num_clips, 1)
        clip_duration = max(clip_duration, 3)  # minimum 3 seconds per clip
        
        # Process and concatenate video clips
        processed_clips = []
        
        for i, clip_path in enumerate(video_clips):
            clip = process_video_clip(clip_path, clip_duration)
            if clip:
                processed_clips.append(clip)
        
        if not processed_clips:
            print("No clips processed, creating color background")
            bg = ColorClip(
                size=(WIDTH, HEIGHT),
                color=[0, 0, 0],
                duration=total_duration
            )
            processed_clips = [bg]
        
        # Concatenate all clips
        if len(processed_clips) > 1:
            final_video = concatenate_videoclips(
                processed_clips,
                method="compose"
            )
        else:
            final_video = processed_clips[0]
        
        # Loop video if shorter than audio
        if final_video.duration < total_duration:
            loops_needed = int(total_duration / final_video.duration) + 1
            final_video = concatenate_videoclips(
                [final_video] * loops_needed,
                method="compose"
            )
        
        # Trim to audio duration
        final_video = final_video.subclip(0, total_duration)
        
        # Add dark overlay for text readability
        dark_overlay = ColorClip(
            size=(WIDTH, HEIGHT),
            color=[0, 0, 0],
            duration=total_duration
        ).set_opacity(0.3)
        
        # Add text overlays
        overlays = [final_video, dark_overlay]
        
        # Hook text (first 4 seconds - big and bold)
        hook_text = script_data.get("hook_text", "")
        if hook_text:
            hook_clip = create_text_clip(
                hook_text,
                duration=4,
                fontsize=70,
                color="yellow",
                position=("center", "center")
            )
            if hook_clip:
                overlays.append(hook_clip.set_start(0))
        
        # Channel watermark
        watermark = create_text_clip(
            "FOLLOW FOR MORE",
            duration=total_duration,
            fontsize=30,
            color="white",
            position=("center", HEIGHT - 150)
        )
        if watermark:
            overlays.append(watermark)
        
        # Compose all layers
        final_composite = CompositeVideoClip(overlays)
        final_composite = final_composite.subclip(0, total_duration)
        
        # Add audio
        final_with_audio = final_composite.set_audio(audio)
        
        # Export video
        print(f"Exporting video to {output_file}...")
        final_with_audio.write_videofile(
            output_file,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile="temp_audio.m4a",
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        print(f"Video exported successfully: {output_file}")
        return True
        
    except Exception as e:
        print(f"Video assembly error: {e}")
        return False

def make_video():
    """Main function to create YouTube Short"""
    print("=" * 50)
    print("Creating YouTube Short...")
    print("=" * 50)
    
    # Load script data
    try:
        with open("script.json", "r", encoding="utf-8") as f:
            script_data = json.load(f)
    except Exception as e:
        print(f"Error loading script: {e}")
        return False
    
    topic = script_data.get("selected_topic", "india trending")
    print(f"Creating video for: {topic}")
    
    # Download stock videos
    video_clips = download_stock_videos(topic, num_videos=6)
    
    if not video_clips:
        print("No clips downloaded")
        return False
    
    # Create the Short
    success = create_shorts_video(
        script_data,
        video_clips,
        "output_video.mp4"
    )
    
    if success:
        print("\nVideo creation complete!")
        print("File: output_video.mp4")
        return True
    
    return False

if __name__ == "__main__":
    result = make_video()
    if result:
        print("\nVideo ready for CapCut editing!")
    else:
        print("\nVideo creation failed")
