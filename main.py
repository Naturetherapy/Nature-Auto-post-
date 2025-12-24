import requests
import random
import os

# API Keys from GitHub Secrets
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Strict Topic List
STRICT_TOPICS = [
    "lush green nature", "peaceful greenery", "fresh green landscape", 
    "green hills fog", "village greenery", "rain forest green", "calm green background"
]

def get_unique_video():
    query = random.choice(STRICT_TOPICS)
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=20&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers).json()
    
    if not os.path.exists('posted_videos.txt'):
        with open('posted_videos.txt', 'w') as f: f.write("")
    
    with open('posted_videos.txt', 'r') as f:
        posted_ids = f.read().splitlines()

    videos = response.get('videos', [])
    for vid in videos:
        if str(vid['id']) not in posted_ids:
            with open('posted_videos.txt', 'a') as f:
                f.write(str(vid['id']) + '\n')
            # Picking the best HD link
            video_link = next(f['link'] for f in vid['video_files'] if f['quality'] == 'hd' or f['quality'] == 'sd')
            return video_link, query
    return None, None

def post_content():
    video_url, topic = get_unique_video()
    if not video_url:
        print("No new video found.")
        return

    # Title, Description and Exactly 8 Hashtags
    title = f"Pure {topic.title()}"
    description = f"🌿 {title}\n\nExperience the healing power of lush green nature. Fresh vibes for your soul. ✨"
    hashtags = "#nature #greenery #peaceful #landscape #forest #fresh #serenity #naturelovers"
    full_caption = f"{description}\n\n{hashtags}"

    # 1. Trigger Telegram
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                  data={"chat_id": TELEGRAM_CHAT_ID, "video": video_url, "caption": full_caption})

    # 2. Trigger Make.com Webhook (Automatic Social Media Post)
    payload = {
        "video_url": video_url,
        "title": title,
        "caption": full_caption,
        "hashtags": hashtags
    }
    response = requests.post(MAKE_WEBHOOK_URL, json=payload)
    
    if response.status_code == 200:
        print(f"Success: Posted {topic} to Telegram & Make.com")
    else:
        print(f"Error triggering Make.com: {response.status_code}")

if __name__ == "__main__":
    post_content()
