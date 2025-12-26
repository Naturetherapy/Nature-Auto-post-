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

STRICT_TOPICS = [
    "deep ocean waves white foam no people", "crystal clear waterfall rocks no bridge",
    "underwater coral reef fish", "frozen lake ice patterns", "mountain stream forest rocks",
    "misty pine forest aerial", "rainforest canopy bird eye view", "autumn leaves macro texture",
    "wildflower meadow no fence", "bamboo grove sunlight", "snowy mountain peaks blue sky",
    "desert sand dunes wind", "red rock deep canyon", "volcanic lava landscape raw earth",
    "arctic glacier blue ice", "moving clouds timelapse sky", "northern lights aurora borealis",
    "sunlight rays through forest trees"
]

HASHTAGS = "# shorts #nature #wildlife #serenity #earth #landscape #adventure #explore #greenery #scenery #wildlifephotography"
HISTORY_FILE = "posted_history.txt"

def get_history():
    """History file se purani IDs load karna"""
    if not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f: return f.read().splitlines()

def save_to_history(v_id, a_id):
    """Nayi IDs save karna"""
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{v_id}\n{a_id}\n")

def get_unique_music(history):
    """Naya aur unique background music dhoondna [cite: 2025-12-23]"""
    try:
        r_page = random.randint(1, 60)
        # Nature ambient music search [cite: 2025-12-23]
        url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient&token={FREESOUND_API_KEY}&filter=duration:[10 TO 20]&fields=id,previews&page={r_page}"
        resp = requests.get(url, timeout=10).json()
        results = resp.get('results', [])
        random.shuffle(results)
        
        for track in results:
            t_id = str(track['id'])
            if t_id not in history: # Music Repetition Check
                m_url = track['previews']['preview-hq-mp3']
                r = requests.get(m_url, timeout=15)
                with open("m.mp3", "wb") as f: f.write(r.content)
                return "m.mp3", t_id
    except: return None, None

def fast_merge(v_path, m_path, out_path):
    """Video aur Audio ko physically merge karna"""
    try:
        # '-c:v copy' speed ke liye aur '-c:a aac' compatibility ke liye
        cmd = [
            'ffmpeg', '-y', '-i', v_path, '-i', m_path,
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
            '-shortest', '-preset', 'ultrafast', out_path
        ]
        subprocess.run(cmd, check=True, timeout=25)
        return os.path.exists(out_path)
    except: return False

def run_automation():
    start_time = time.time()
    history = get_history()
    topic = random.choice(STRICT_TOPICS)
    
    # 1. Unique HD Video Selection
    v_url_api = f"https://api.pexels.com/videos/search?query={topic}&per_page=20&orientation=portrait"
    v_resp = requests.get(v_url_api, headers={"Authorization": PEXELS_API_KEY}, timeout=10).json()
    
    for vid in v_resp.get('videos', []):
        v_id = str(vid['id'])
        # Duration aur Repetition check
        if v_id not in history and 10 <= vid.get('duration', 0) <= 20:
            # 1080p (HD) link pick karna
            v_link = next((f['link'] for f in vid['video_files'] if f['width'] >= 1080), vid['video_files'][0]['link'])
            
            # 2. Get Music [cite: 2025-12-23]
            music_file, a_id = get_unique_music(history)
            
            if music_file and fast_merge(v_link, music_file, "final.mp4"):
                # 3. Upload to Catbox for Webhook URL
                with open("final.mp4", 'rb') as f:
                    up = requests.post('https://catbox.moe/user/api.php', data={'reqtype': 'fileupload'}, files={'fileToUpload': f}, timeout=30)
                    merged_url = up.text.strip() if up.status_code == 200 else None

                if merged_url:
                    caption = f"🎬 Nature Magic: {topic.title()}\n\n{HASHTAGS}"
                    
                    # Telegram delivery
                    with open("final.mp4", 'rb') as f:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": f})
                    
                    # Make.com Webhook delivery
                    if MAKE_WEBHOOK_URL:
                        requests.post(MAKE_WEBHOOK_URL, json={"video_url": merged_url, "caption": caption})
                    
                    # IDs Save karein
                    save_to_history(v_id, a_id)
                    print(f"Success! Time: {time.time()-start_time:.2f}s")
                    return

if __name__ == "__main__":
    run_automation()
