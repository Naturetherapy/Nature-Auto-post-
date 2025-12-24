import requests
import random
import os

# API Keys (GitHub Secrets)
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Aapke STRICT Nature Topics
STRICT_TOPICS = [
    "lush green nature", "peaceful greenery", "fresh green landscape", 
    "green hills fog", "village greenery", "rain forest green", "calm green background"
]

def get_real_video():
    query = random.choice(STRICT_TOPICS)
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers).json()
        if not os.path.exists('posted_videos.txt'):
            open('posted_videos.txt', 'w').close()
        
        with open('posted_videos.txt', 'r') as f:
            posted_ids = f.read().splitlines()

        videos = response.get('videos', [])
        for vid in videos:
            if str(vid['id']) not in posted_ids:
                video_files = vid.get('video_files', [])
                video_link = next((f['link'] for f in video_files if f['quality'] == 'hd'), video_files[0]['link'])
                
                with open('posted_videos.txt', 'a') as f:
                    f.write(str(vid['id']) + '\n')
                return video_link, query
    except Exception as e:
        print(f"Error: {e}")
    return None, None

def post_now():
    v_url, topic = get_real_video()
    if not v_url: return

    # Exactly 8 Hashtags as requested
    hashtags = "#nature #greenery #peace #forest #landscape #fresh #serenity #naturelovers"
    caption = f"🌿 Pure {topic.title()}\n\nExperience the healing power of greenery. ✨\n\n{hashtags}"

    # Telegram Post
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                  data={"chat_id": TELEGRAM_CHAT_ID, "video": v_url, "caption": caption})

    # Make.com Automatic Post
    if MAKE_WEBHOOK_URL:
        requests.post(MAKE_WEBHOOK_URL, json={"video_url": v_url, "caption": caption})

if __name__ == "__main__":
    post_now()
