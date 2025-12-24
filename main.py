import requests
import random
import os
import moviepy.editor as mp

# API Keys from GitHub Secrets
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Aapke 10 Strict Nature Topics
STRICT_TOPICS = [
    "Wild Green Forests", "Green Mountains", "Natural Valleys", 
    "Rainforests", "Grasslands", "Wildflower Meadows", 
    "Forest Floor Flowers", "Riverbank Vegetation", 
    "Alpine Flowers", "Seasonal Wildflowers"
]

def add_bg_music(video_path, music_path, output_path):
    """Video mein nature background music add karne ke liye"""
    try:
        video = mp.VideoFileClip(video_path)
        # Background music load karna aur video ki length jitna set karna
        audio = mp.AudioFileClip(music_path).set_duration(video.duration)
        final_video = video.set_audio(audio)
        
        # High quality MP4 export
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
        
        video.close()
        audio.close()
        return output_path
    except Exception as e:
        print(f"Music Error: {e}")
        return video_path

def post_content():
    # 1. Random Topic Select Karna
    query = random.choice(STRICT_TOPICS)
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers).json()
        
        # 2. History Check (No Repeats)
        if not os.path.exists('posted_videos.txt'):
            open('posted_videos.txt', 'w').close()
        with open('posted_videos.txt', 'r') as f:
            posted_ids = f.read().splitlines()

        videos = response.get('videos', [])
        for vid in videos:
            if str(vid['id']) not in posted_ids:
                v_url = vid['video_files'][0]['link']
                
                # 3. Real Video Download Karna
                with open("temp.mp4", 'wb') as f:
                    f.write(requests.get(v_url).content)
                
                # 4. Music Merge Karna (Ensure music/nature_bg.mp3 exists in repo)
                processed_file = add_bg_music("temp.mp4", "music/nature_bg.mp3", "final.mp4")
                
                # Exactly 8 Hashtags as requested
                hashtags = "#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"
                caption = f"🌿 {query}\n\nPure nature vibes with background music. ✨\n\n{hashtags}"
                
                # 5. Telegram Post
                with open(processed_file, 'rb') as v:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": v})
                
                # 6. Make.com Automatic Trigger
                if MAKE_WEBHOOK_URL:
                    requests.post(MAKE_WEBHOOK_URL, json={"topic": query, "caption": caption, "video_url": v_url})
                
                # History update karna
                with open('posted_videos.txt', 'a') as f:
                    f.write(str(vid['id']) + '\n')
                
                print(f"Successfully posted: {query}")
                return
    except Exception as e:
        print(f"Main Error: {e}")

if __name__ == "__main__":
    post_content()
