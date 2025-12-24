import requests
import random
import os

# API Keys from GitHub Secrets
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Aapke naye Strict Topics
STRICT_TOPICS = [
    "Wild Green Forests", "Green Mountains", "Natural Valleys", 
    "Rainforests", "Grasslands", "Wildflower Meadows", 
    "Forest Floor Flowers", "Riverbank Vegetation", 
    "Alpine Flowers", "Seasonal Wildflowers"
]

def get_unique_nature_video():
    query = random.choice(STRICT_TOPICS)
    # Background music/nature sound wale videos ke liye search
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=20&orientation=portrait"
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
                # HD link select karna
                video_link = next((f['link'] for f in video_files if f['quality'] == 'hd'), video_files[0]['link'])
                
                with open('posted_videos.txt', 'a') as f:
                    f.write(str(vid['id']) + '\n')
                return video_link, query
    except Exception as e:
        print(f"Error: {e}")
    return None, None

def post_content():
    v_url, topic = get_unique_nature_video()
    if not v_url: return

    # 8 Fixed Hashtags
    hashtags = "#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"
    caption = f"🌿 {topic}\n\nExperience the beauty of nature with soothing background sounds. ✨\n\n{hashtags}"

    # 1. Post to Telegram
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                  data={"chat_id": TELEGRAM_CHAT_ID, "video": v_url, "caption": caption})

    # 2. Post to Make.com Webhook
    if MAKE_WEBHOOK_URL:
        requests.post(MAKE_WEBHOOK_URL, json={"video_url": v_url, "caption": caption, "title": topic})

if __name__ == "__main__":
    post_content()
