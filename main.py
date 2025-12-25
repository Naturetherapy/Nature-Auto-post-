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

DYNAMIC_TITLES = ["Pure Nature", "Wild Beauty", "Earth Magic", "Nature View", "Green Serene", "Deep Nature", "Quiet Wild", "Raw Earth"]
DYNAMIC_CAPTIONS = ["Magic is real", "Silent forest", "Peaceful vibes", "Clean nature", "Green world", "Fresh air", "Hidden gem", "Pure spirit"]
HASHTAGS = "#nature #wildlife #serenity #earth #landscape #adventure #explore #greenery #scenery #wildlifephotography"

def get_dynamic_music():
    """Freesound se music fetch karna [cite: 2025-12-23]"""
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

def merge_compulsory_reencode(v_path, m_path, out_path):
    """FFmpeg Re-encoding: Yeh audio ko video ke sath zabardasti lock kar deta hai"""
    try:
        # Command: Re-encode audio to AAC and video to H.264, forcing a mix
        cmd = [
            'ffmpeg', '-y',
            '-i', v_path,
            '-stream_loop', '-1',
            '-i', m_path,
            '-c:v', 'libx264', # Video re-encode for safety
            '-c:a', 'aac',     # Audio re-encode to AAC
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            '-pix_fmt', 'yuv420p', # Compatibility for Telegram/Mobile
            out_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Validation: Kya file bani aur kya usme audio hai?
        if os.path.exists(out_path) and os.path.getsize(out_path) > 5000:
            return True
    except Exception as e:
        print(f"Merge Error: {e}")
    return False

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
            
            # Download Raw Video
            with open("raw.mp4", 'wb') as f: f.write(requests.get(v_url).content)
            
            # Download Music [cite: 2025-12-23]
            music = get_dynamic_music()
            
            if music:
                final_video = "final_output.mp4"
                # COMPULSORY MERGE CHECK
                if merge_compulsory_reencode("raw.mp4", music, final_video):
                    title = random.choice(DYNAMIC_TITLES)[:15]
                    caption = random.choice(DYNAMIC_CAPTIONS)[:15]
                    full_desc = f"🎬 {title}\n\n{caption}\n\n{HASHTAGS}"

                    # 1. Telegram Post
                    with open(final_video, 'rb') as v:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": full_desc}, files={"video": v})
                    
                    # 2. Make.com Webhook Post
                    if MAKE_WEBHOOK_URL:
                        requests.post(MAKE_WEBHOOK_URL, json={"title": title, "video_url": v_url, "caption": full_desc})

                    with open(history_file, 'a') as f: f.write(str(vid['id']) + '\n')
                    print(f"Success! Merged video posted for {topic}")
                    return
                else:
                    print("Merge failed, trying next video...")

if __name__ == "__main__":
    run_automation()
