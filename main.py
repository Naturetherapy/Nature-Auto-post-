import requests
import random
import os
import subprocess

# API Keys aur Configuration
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

DYNAMIC_TITLES = ["Pure Nature", "Wild Beauty", "Earth Magic", "Nature View", "Green Serene", "Deep Nature", "Quiet Wild", "Raw Earth"]
DYNAMIC_CAPTIONS = ["Magic is real", "Silent forest", "Peaceful vibes", "Clean nature", "Green world", "Fresh air", "Hidden gem", "Pure spirit"]
HASHTAGS = "#nature #wildlife #serenity #earth #landscape #adventure #explore #greenery #scenery #wildlifephotography"

def get_dynamic_music():
    """Freesound.org se music download [cite: 2025-12-23]"""
    try:
        r_page = random.randint(1, 100)
        url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient+birds&token={FREESOUND_API_KEY}&filter=duration:[10 TO 60]&fields=id,previews&page={r_page}"
        resp = requests.get(url).json()
        results = resp.get('results', [])
        if results:
            music_url = random.choice(results)['previews']['preview-hq-mp3']
            r = requests.get(music_url, stream=True)
            with open("bg_music.mp3", "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: f.write(chunk)
            return "bg_music.mp3"
    except: return None

def upload_and_get_url(file_path):
    """Merged file ko upload karke uska URL lena"""
    try:
        with open(file_path, 'rb') as f:
            # File.io par upload (yeh 1-2 hafte tak valid rehta hai)
            response = requests.post('https://file.io', files={'file': f})
            return response.json().get('link')
    except: return None

def merge_now(v_path, m_path, out_path):
    """FFmpeg Physical Merge"""
    try:
        cmd = [
            'ffmpeg', '-y', '-i', v_path, '-stream_loop', '-1', '-i', m_path,
            '-c:v', 'libx264', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
            '-shortest', '-pix_fmt', 'yuv420p', out_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return os.path.exists(out_path)
    except: return False

def run_automation():
    topic = random.choice(STRICT_TOPICS)
    history_file = 'posted_videos.txt'
    if not os.path.exists(history_file): open(history_file, 'w').close()
    with open(history_file, 'r') as f: posted_ids = f.read().splitlines()

    v_resp = requests.get(f"https://api.pexels.com/videos/search?query={topic}&per_page=40&orientation=portrait", 
                          headers={"Authorization": PEXELS_API_KEY}).json()
    videos = v_resp.get('videos', [])
    random.shuffle(videos)

    for vid in videos:
        if str(vid['id']) not in posted_ids and 5 <= vid.get('duration', 0) <= 15:
            v_url = next(f['link'] for f in vid['video_files'] if f['width'] >= 720)
            with open("raw.mp4", 'wb') as f: f.write(requests.get(v_url).content)
            
            music = get_dynamic_music()
            if music:
                final_video = "final_merged.mp4"
                if merge_now("raw.mp4", music, final_video):
                    # Step 1: Merged video ka URL banayein
                    merged_url = upload_and_get_url(final_video)
                    
                    if merged_url:
                        title = random.choice(DYNAMIC_TITLES)[:15]
                        caption = random.choice(DYNAMIC_CAPTIONS)[:15]
                        full_desc = f"🎬 {title}\n\n{caption}\n\n{HASHTAGS}"

                        # 2. Telegram: Direct File
                        with open(final_video, 'rb') as v:
                            requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                          data={"chat_id": TELEGRAM_CHAT_ID, "caption": full_desc}, files={"video": v})
                        
                        # 3. Webhook: SENDING MERGED URL
                        if MAKE_WEBHOOK_URL:
                            payload = {
                                "title": title,
                                "video_url": merged_url, # Ab merged wala link jayega
                                "caption": full_desc
                            }
                            requests.post(MAKE_WEBHOOK_URL, json=payload)

                        with open(history_file, 'a') as f: f.write(str(vid['id']) + '\n')
                        return

if __name__ == "__main__":
    run_automation()
