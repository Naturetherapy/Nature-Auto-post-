import requests
import random
import os
# Moviepy ke naye versions ke liye updated import
from moviepy import VideoFileClip, AudioFileClip

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Aapke bataye gaye 10 Strict Topics
STRICT_TOPICS = [
    "Wild Green Forests", "Green Mountains", "Natural Valleys", 
    "Rainforests", "Grasslands", "Wildflower Meadows", 
    "Forest Floor Flowers", "Riverbank Vegetation", 
    "Alpine Flowers", "Seasonal Wildflowers"
]

def add_bg_music(video_path, music_path, output_path):
    try:
        video = VideoFileClip(video_path)
        # Background music add karna (video ki duration tak)
        audio = AudioFileClip(music_path).with_duration(video.duration)
        final_video = video.shell_audio(audio) if hasattr(video, 'shell_audio') else video.set_audio(audio)
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        video.close()
        audio.close()
        return output_path
    except Exception as e:
        print(f"Music Error: {e}")
        return video_path

def get_video():
    query = random.choice(STRICT_TOPICS)
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    
    resp = requests.get(url, headers=headers).json()
    if not os.path.exists('posted_videos.txt'): open('posted_videos.txt', 'w').close()
    with open('posted_videos.txt', 'r') as f: posted_ids = f.read().splitlines()

    for vid in resp.get('videos', []):
        if str(vid['id']) not in posted_ids:
            v_url = vid['video_files'][0]['link']
            # Video download karna
            with open("temp.mp4", 'wb') as f: f.write(requests.get(v_url).content)
            
            # Music merge karna (music/nature_bg.mp3 file honi chahiye)
            processed_file = add_bg_music("temp.mp4", "music/nature_bg.mp3", "final.mp4")
            
            with open('posted_videos.txt', 'a') as f: f.write(str(vid['id']) + '\n')
            return processed_file, query
    return None, None

if __name__ == "__main__":
    file, topic = get_video()
    if file:
        hashtags = "#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"
        caption = f"🌿 {topic}\n\nPure nature vibes with background music. ✨\n\n{hashtags}"
        
        # Telegram Post
        with open(file, 'rb') as v:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                          data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": v})
        
        # Make.com Trigger
        if MAKE_WEBHOOK_URL:
            requests.post(MAKE_WEBHOOK_URL, json={"topic": topic, "caption": caption})
