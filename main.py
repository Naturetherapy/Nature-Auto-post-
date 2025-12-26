import requests, random, os, subprocess, time

# API Keys & Config
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
FREESOUND_API_KEY = os.getenv('FREESOUND_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

HISTORY_FILE = "posted_history.txt"
# Aapke fixed hashtags
FIXED_HASHTAGS = "# shorts #nature #wildlife #serenity #earth #landscape #adventure #explore #scenery"

STRICT_TOPICS = [
    "deep ocean waves", "crystal clear waterfall", "underwater coral reef",
    "misty pine forest", "rainforest canopy", "snowy mountain peaks",
    "desert sand dunes", "arctic glacier", "sunlight rays forest"
]

def get_history():
    if not os.path.exists(HISTORY_FILE): return []
    with open(HISTORY_FILE, "r") as f: return f.read().splitlines()

def save_to_history(v_id, a_id):
    with open(HISTORY_FILE, "a") as f: f.write(f"{v_id}\n{a_id}\n")

def get_dynamic_metadata(topic):
    """Title aur Description har baar badlega"""
    adjectives = ["Peaceful", "Majestic", "Wild", "Pure", "Calm", "Serene", "Mystic"]
    title = f"{random.choice(adjectives)} {topic.title()} View".strip()[:50]
    description = f"Experience the raw beauty of {topic}. Pure relaxation."
    return title, description

def get_unique_music(history):
    """Broad search taaki NoneType error na aaye"""
    try:
        r_page = random.randint(1, 50)
        url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient&token={FREESOUND_API_KEY}&filter=duration:[10 TO 25]&fields=id,previews&page={r_page}"
        resp = requests.get(url, timeout=10).json()
        results = resp.get('results', [])
        if not results: return None, None
        random.shuffle(results)
        for track in results:
            t_id = str(track['id'])
            if t_id not in history:
                m_url = track['previews']['preview-hq-mp3']
                r = requests.get(m_url, timeout=15)
                with open("m.mp3", "wb") as f: f.write(r.content)
                return "m.mp3", t_id
    except: pass
    return None, None

def run_automation():
    start_time = time.time()
    history = get_history()
    topic = random.choice(STRICT_TOPICS)
    title, description = get_dynamic_metadata(topic)
    
    # 1. HD Video Fetch
    v_resp = requests.get(f"https://api.pexels.com/videos/search?query={topic}&per_page=15&orientation=portrait", 
                          headers={"Authorization": PEXELS_API_KEY}, timeout=10).json()
    
    for vid in v_resp.get('videos', []):
        v_id = str(vid['id'])
        if v_id not in history and 10 <= vid.get('duration', 0) <= 25:
            v_link = next((f['link'] for f in vid['video_files'] if f['width'] >= 1080), vid['video_files'][0]['link'])
            
            # 2. Music Fetch [cite: 2025-12-23]
            music_file, a_id = get_unique_music(history)
            if not music_file: continue 
            
            # 3. Fast Combine & Delivery
            cmd = ['ffmpeg', '-y', '-i', v_link, '-i', music_file, '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0', '-shortest', '-preset', 'ultrafast', 'final.mp4']
            subprocess.run(cmd, check=True, timeout=30)
            
            if os.path.exists("final.mp4"):
                with open("final.mp4", 'rb') as f:
                    up = requests.post('https://catbox.moe/user/api.php', data={'reqtype': 'fileupload'}, files={'fileToUpload': f}, timeout=30)
                    merged_url = up.text.strip()
                
                if merged_url.startswith('http'):
                    # Caption mein Title, Description dynamic hain, Hashtags fix hain
                    caption = f"🎬 {title}\n\n{description}\n\n{FIXED_HASHTAGS}"
                    
                    # Telegram & Webhook Delivery
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"video": open("final.mp4", 'rb')})
                    
                    if MAKE_WEBHOOK_URL:
                        requests.post(MAKE_WEBHOOK_URL, json={"video_url": merged_url, "caption": caption})
                    
                    save_to_history(v_id, a_id)
                    print(f"Success! Posted: {title}")
                    return

if __name__ == "__main__":
    run_automation()
