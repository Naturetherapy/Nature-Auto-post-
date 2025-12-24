import requests
import random
import os
import moviepy.editor as mp
from moviepy.audio.fx.all import audio_loop

# API Keys from GitHub Secrets
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
FREESOUND_API_KEY = os.getenv('FREESOUND_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

STRICT_TOPICS = [
    "Wild Green Forests", "Green Mountains", "Natural Valleys", 
    "Rainforests", "Grasslands", "Wildflower Meadows", 
    "Forest Floor Flowers", "Riverbank Vegetation", 
    "Alpine Flowers", "Seasonal Wildflowers"
]

def get_dynamic_music():
    """Freesound.org se dynamic nature music fetch karna [cite: 2025-12-23]"""
    url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient+soothing&token={FREESOUND_API_KEY}&filter=duration:[10 TO 120]&fields=id,previews"
    try:
        resp = requests.get(url).json()
        results = resp.get('results', [])
        if results:
            sound = random.choice(results)
            music_url = sound['previews']['preview-hq-mp3']
            with open("dynamic_music.mp3", "wb") as f:
                f.write(requests.get(music_url).content)
            return "dynamic_music.mp3"
    except Exception as e:
        print(f"Music Fetch Error: {e}")
    return None

def add_bg_music(video_path, music_path, output_path):
    """Audio Looping ke saath music merge karna taaki duration error na aaye"""
    try:
        video = mp.VideoFileClip(video_path)
        audio = mp.AudioFileClip(music_path)
        
        # Agar music chhota hai toh use loop karna
        if audio.duration < video.duration:
            audio = audio_loop(audio, duration=video.duration)
        else:
            audio = audio.set_duration(video.duration)
            
        final_video = video.set_audio(audio)
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
        video.close()
        audio.close()
        return output_path
    except Exception as e:
        print(f"Processing Error: {e}")
        return video_path

def run_automation():
    topic = random.choice(STRICT_TOPICS)
    v_url = f"https://api.pexels.com/videos/search?query={topic}&per_page=20&orientation=portrait"
    v_resp = requests.get(v_url, headers={"Authorization": PEXELS_API_KEY}).json()
    
    if not os.path.exists('posted_videos.txt'): open('posted_videos.txt', 'w').close()
    with open('posted_videos.txt', 'r') as f: posted_ids = f.read().splitlines()

    for vid in v_resp.get('videos', []):
        if str(vid['id']) not in posted_ids:
            # Download Media
            with open("temp.mp4", 'wb') as f: f.write(requests.get(vid['video_files'][0]['link']).content)
            music_file = get_dynamic_music()
            
            if music_file:
                processed_file = add_bg_music("temp.mp4", music_file, "final.mp4")
                
                # Exactly 8 hashtags
                hashtags = "#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"
                caption = f"🌿 {topic}\n\nPure nature vibes with dynamic background music. ✨\n\n{hashtags}"
                
                # 1. Telegram Delivery
                with open(processed_file, 'rb') as v:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": v})
                
                # 2. Make.com Delivery
                if MAKE_WEBHOOK_URL:
                    requests.post(MAKE_WEBHOOK_URL, json={"topic": topic, "caption": caption, "video_url": vid['video_files'][0]['link']})
                
                with open('posted_videos.txt', 'a') as f: f.write(str(vid['id']) + '\n')
                return

if __name__ == "__main__":
    run_automation()
