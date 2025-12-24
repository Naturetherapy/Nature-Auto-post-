import requests
import random
import os

# API Keys from GitHub Secrets
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

STRICT_TOPICS = [
    "lush green nature", "peaceful greenery", "fresh green landscape", 
    "green hills fog", "village greenery", "rain forest green", "calm green background"
]

def get_unique_video():
    query = random.choice(STRICT_TOPICS)
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=20&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers).json()
        
        if not os.path.exists('posted_videos.txt'):
            with open('posted_videos.txt', 'w') as f: f.write("")
        
        with open('posted_videos.txt', 'r') as f:
            posted_ids = f.read().splitlines()

        videos = response.get('videos', [])
        for vid in videos:
            if str(vid['id']) not in posted_ids:
                # Fix for StopIteration: Try to find HD/SD, else take any first link
                video_files = vid.get('video_files', [])
                if not video_files: continue
                
                # Pehle HD/SD dhoondo, nahi toh jo bhi pehla link hai le lo
                video_link = None
                for f in video_files:
                    if f.get('quality') in ['hd', 'sd']:
                        video_link = f['link']
                        break
                
                if not video_link:
                    video_link = video_files[0]['link']

                with open('posted_videos.txt', 'a') as f:
                    f.write(str(vid['id']) + '\n')
                
                return video_link, query
    except Exception as e:
        print(f"Error fetching video: {e}")
        
    return None, None

def post_content():
    video_url, topic = get_unique_video()
    if not video_url:
        print("No suitable new video found.")
        return

    title = f"Pure {topic.title()}"
    # Title + Description + 8 Hashtags
    hashtags = "#nature #greenery #peaceful #landscape #forest #fresh #serenity #naturelovers"
    full_caption = f"🌿 {title}\n\nExperience the healing power of lush green nature. Fresh vibes for your soul. ✨\n\n{hashtags}"

    # 1. Telegram Post
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                  data={"chat_id": TELEGRAM_CHAT_ID, "video": video_url, "caption": full_caption})

    # 2. Make.com Webhook Post
    if MAKE_WEBHOOK_URL:
        payload = {"video_url": video_url, "title": title, "caption": full_caption, "hashtags": hashtags}
        requests.post(MAKE_WEBHOOK_URL, json=payload)
        print("Triggered Make.com Webhook")
    else:
        print("Warning: MAKE_WEBHOOK_URL is missing!")

if __name__ == "__main__":
    post_content()
