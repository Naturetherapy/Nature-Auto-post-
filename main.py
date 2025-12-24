import requests
import random
import os
from moviepy.editor import VideoFileClip, AudioFileClip

# API Keys
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

STRICT_TOPICS = [
    "Wild Green Forests", "Green Mountains", "Natural Valleys", 
    "Rainforests", "Grasslands", "Wildflower Meadows", 
    "Forest Floor Flowers", "Riverbank Vegetation", 
    "Alpine Flowers", "Seasonal Wildflowers"
]

def add_background_music(video_path, music_path, output_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(music_path).subclip(0, video.duration)
    # Music add karna aur volume set karna
    final_video = video.set_audio(audio)
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

def get_video_and_process():
    query = random.choice(STRICT_TOPICS)
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    
    response = requests.get(url, headers=headers).json()
    videos = response.get('videos', [])
    
    # Repeat check logic
    if not os.path.exists('posted_videos.txt'): open('posted_videos.txt', 'w').close()
    with open('posted_videos.txt', 'r') as f: posted_ids = f.read().splitlines()

    for vid in videos:
        if str(vid['id']) not in posted_ids:
            v_url = vid['video_files'][0]['link']
            
            # Video download karna editing ke liye
            with open("temp_video.mp4", 'wb') as f:
                f.write(requests.get(v_url).content)
            
            # Background Music add karna
            final_file = add_background_music("temp_video.mp4", "music/nature_bg.mp3", "final_output.mp4")
            
            with open('posted_videos.txt', 'a') as f: f.write(str(vid['id']) + '\n')
            return "final_output.mp4", query

    return None, None

def post_all():
    file_path, topic = get_video_and_process()
    if not file_path: return

    hashtags = "#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"
    caption = f"🌿 {topic}\n\nPure nature vibes with soothing background music. ✨\n\n{hashtags}"

    # Telegram Post (Local File)
    with open(file_path, 'rb') as video:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": video})

    # Make.com Post (File link ke liye aapko cloud storage chahiye hoga, ya caption bhej sakte hain)
    if MAKE_WEBHOOK_URL:
        requests.post(MAKE_WEBHOOK_URL, json={"topic": topic, "caption": caption, "status": "Video processed with music"})

if __name__ == "__main__":
    post_all()
