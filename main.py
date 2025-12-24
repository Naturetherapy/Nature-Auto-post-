import requests
import random
import os

# API Keys
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Aapke Strict Topics
STRICT_TOPICS = [
    "lush green nature", "peaceful greenery", "fresh green landscape", 
    "green hills fog", "village greenery", "rain forest green", "calm green background"
]

def get_new_video():
    query = random.choice(STRICT_TOPICS)
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers).json()
    
    # History check karne ke liye (Repeated videos rokne ke liye)
    if not os.path.exists('posted_videos.txt'):
        open('posted_videos.txt', 'w').close()
    
    with open('posted_videos.txt', 'r') as f:
        posted_ids = f.read().splitlines()

    videos = response.get('videos', [])
    for vid in videos:
        if str(vid['id']) not in posted_ids:
            # Video mil gaya jo pehle post nahi hua
            with open('posted_videos.txt', 'a') as f:
                f.write(str(vid['id']) + '\n')
            
            # Best quality video file nikalna
            video_file = vid['video_files'][0]['link']
            return video_file, query

    return None, None

def post_now(video_url, topic):
    caption = f"🌿 {topic.title()}\n\nExperience the serenity of nature. ✨\n\n#nature #greenery #peace #environment"
    
    # 1. Telegram Post
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    requests.post(tg_url, data={"chat_id": TELEGRAM_CHAT_ID, "video": video_url, "caption": caption})
    
    # 2. Make.com Webhook Post
    payload = {"video_url": video_url, "topic": topic, "caption": caption}
    requests.post(MAKE_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    v_url, v_topic = get_new_video()
    if v_url:
        post_now(v_url, v_topic)
        print(f"Successfully posted: {v_topic}")
    else:
        print("No new videos found.")
