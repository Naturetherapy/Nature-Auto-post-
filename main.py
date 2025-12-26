import requests
import random
import os
import subprocess
import time

# API Keys aur Configuration
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
FREESOUND_API_KEY = os.getenv('FREESOUND_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Saare 18 Strict Nature Topics
STRICT_TOPICS = [
    "deep ocean waves white foam no people", "crystal clear waterfall rocks no bridge",
    "underwater coral reef fish", "frozen lake ice patterns", "mountain stream forest rocks",
    "misty pine forest aerial", "rainforest canopy bird eye view", "autumn leaves macro texture",
    "wildflower meadow no fence", "bamboo grove sunlight", "snowy mountain peaks blue sky",
    "desert sand dunes wind", "red rock deep canyon", "volcanic lava landscape raw earth",
    "arctic glacier blue ice", "moving clouds timelapse sky", "northern lights aurora borealis",
    "sunlight rays through forest trees"
]

HASHTAGS = "#naHASHTAGS = "#shorts #nature #wildlife #serenity #earth #landscape #adventure #explore #greenery #scenery #wildl

def get_fast_music():
    """Freesound se background music fetch karna [cite: 2025-12-23]"""
    try:
        r_page = random.randint(1, 50)
        url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient&token={FREESOUND_API_KEY}&filter=duration:[10 TO 20]&fields=previews&page={r_page}&page_size=1"
        resp = requests.get(url, timeout=7).json()
        music_url = resp['results'][0]['previews']['preview-hq-mp3']
        r = requests.get(music_url, stream=True, timeout=10)
        with open("m.mp3", "wb") as f:
            for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        return "m.mp3"
    except: return None

def upload_video(file_path):
    """Stable upload taaki Webhook ko valid URL mile"""
    # Catbox is more stable for Instagram API
    try:
        with open(file_path, 'rb') as f:
            r = requests.post('https://catbox.moe/user/api.php', data={'reqtype': 'fileupload'}, files={'fileToUpload': f}, timeout=25)
            if r.status_code == 200 and r.text.startswith('http'):
                return r.text.strip()
    except: pass
    return None

def fast_merge(v_path, m_path, out_path):
    """AAC audio merge with Ultrafast preset"""
    try:
        # '-preset ultrafast' merging speed badhata hai
        cmd = [
            'ffmpeg', '-y', '-i', v_path, '-i', m_path,
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
            '-shortest', '-preset', 'ultrafast', out_path
        ]
        subprocess.run(cmd, check=True, timeout=20)
        return os.path.exists(out_path)
    except: return False

def run_automation():
    start = time.time()
    topic = random.choice(STRICT_TOPICS)
    
    # 1. High Quality Video Fetch (Fixes 'File too small' error)
    v_resp = requests.get(f"https://api.pexels.com/videos/search?query={topic}&per_page=5&orientation=portrait", 
                          headers={"Authorization": PEXELS_API_KEY}, timeout=10).json()
    
    for vid in v_resp.get('videos', []):
        # 10-15 seconds duration for stability
        if 10 <= vid.get('duration', 0) <= 15:
            # Picking 1080p link
            v_url = next((f['link'] for f in vid['video_files'] if f['width'] >= 1080), vid['video_files'][0]['link'])
            with open("v.mp4", 'wb') as f: f.write(requests.get(v_url, timeout=20).content)
            
            # 2. Music & Merge [cite: 2025-12-23]
            music = get_fast_music()
            if music and fast_merge("v.mp4", music, "final.mp4"):
                
                caption = f"🎬 Pure Nature Magic\n\n{HASHTAGS}"
                
                # 3. Parallel Delivery
                # Telegram (Direct Merged File)
                with open("final.mp4", 'rb') as f:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": f}, timeout=20)
                
                # Webhook (Catbox URL for Make.com)
                merged_url = upload_video("final.mp4")
                if merged_url and MAKE_WEBHOOK_URL:
                    requests.post(MAKE_WEBHOOK_URL, json={"video_url": merged_url, "caption": caption}, timeout=15)
                
                print(f"Success! Total Time: {time.time()-start:.2f}s")
                return

if __name__ == "__main__":
    run_automation()
