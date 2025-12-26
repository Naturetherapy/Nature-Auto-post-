import requests
import random
import os
import subprocess
import time

# API Keys
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
FREESOUND_API_KEY = os.getenv('FREESOUND_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Aapke saare 18 Strict Topics
STRICT_TOPICS = [
    "deep ocean waves white foam no people", "crystal clear waterfall rocks no bridge",
    "underwater coral reef fish", "frozen lake ice patterns", "mountain stream forest rocks",
    "misty pine forest aerial", "rainforest canopy bird eye view", "autumn leaves macro texture",
    "wildflower meadow no fence", "bamboo grove sunlight", "snowy mountain peaks blue sky",
    "desert sand dunes wind", "red rock deep canyon", "volcanic lava landscape raw earth",
    "arctic glacier blue ice", "moving clouds timelapse sky", "northern lights aurora borealis",
    "sunlight rays through forest trees"
]

DYNAMIC_TITLES = ["Pure Nature", "Wild Beauty", "Earth Magic", "Nature View", "Green Serene", "Deep Nature", "Quiet Wild", "Raw Earth"]
DYNAMIC_CAPTIONS = ["Magic is real", "Silent forest", "Peaceful vibes", "Clean nature", "Green world", "Fresh air", "Hidden gem", "Pure spirit"]
HASHTAGS = "#nature #wildlife #serenity #earth #landscape #adventure #explore #greenery #scenery #wildlifephotography"

def get_fast_music():
    """Freesound se turant music fetch (< 5 sec) [cite: 2025-12-23]"""
    try:
        r_page = random.randint(1, 50)
        url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient&token={FREESOUND_API_KEY}&filter=duration:[10 TO 20]&fields=previews&page={r_page}&page_size=1"
        resp = requests.get(url, timeout=5).json()
        music_url = resp['results'][0]['previews']['preview-hq-mp3']
        r = requests.get(music_url, stream=True, timeout=5)
        with open("m.mp3", "wb") as f:
            for chunk in r.iter_content(chunk_size=4096): f.write(chunk)
        return "m.mp3"
    except: return None

def fast_merge(v_path, m_path, out_path):
    """Super fast merge logic using ultrafast preset"""
    try:
        # '-preset ultrafast' merging speed ko 10 second ke andar le aata hai
        cmd = [
            'ffmpeg', '-y', '-i', v_path, '-i', m_path,
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
            '-shortest', '-preset', 'ultrafast', out_path
        ]
        subprocess.run(cmd, check=True, timeout=15)
        return os.path.exists(out_path)
    except: return False

def run_automation():
    start_all = time.time()
    topic = random.choice(STRICT_TOPICS)
    
    # 1. Pexels Video (Speed Optimization)
    v_resp = requests.get(f"https://api.pexels.com/videos/search?query={topic}&per_page=5&orientation=portrait", 
                          headers={"Authorization": PEXELS_API_KEY}, timeout=7).json()
    v_url = v_resp['videos'][0]['video_files'][0]['link']
    with open("v.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=10).content)
    
    # 2. Get Music & Merge [cite: 2025-12-23]
    music = get_fast_music()
    if music and fast_merge("v.mp4", music, "final.mp4"):
        
        # 3. Parallel Delivery Start
        title = random.choice(DYNAMIC_TITLES)[:15]
        caption = random.choice(DYNAMIC_CAPTIONS)[:15]
        full_desc = f"🎬 {title}\n\n{caption}\n\n{HASHTAGS}"

        # Telegram: Merged video file bhejna
        with open("final.mp4", 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                          data={"chat_id": TELEGRAM_CHAT_ID, "caption": full_desc}, files={"video": f}, timeout=15)
        
        # Webhook: Merged video ka URL upload karke bhejna
        with open("final.mp4", 'rb') as f:
            # file.io turant download link deta hai
            up_resp = requests.post('https://file.io', files={'file': f}, timeout=10).json()
            merged_url = up_resp.get('link')
        
        if merged_url and MAKE_WEBHOOK_URL:
            # Webhook ko ab video_url field mein music wala link milega
            requests.post(MAKE_WEBHOOK_URL, json={"video_url": merged_url, "caption": full_desc}, timeout=5)

    print(f"Total Workflow Completed in: {time.time() - start_all:.2f} seconds")

if __name__ == "__main__":
    run_automation()
