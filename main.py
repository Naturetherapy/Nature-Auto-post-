import requests
import random
import os
import time
import moviepy.editor as mp
from moviepy.audio.fx.all import audio_loop

# API Keys aur Webhook
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
FREESOUND_API_KEY = os.getenv('FREESOUND_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Aapke 18 Ultra-Strict Nature Topics
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
    """Freesound se random music fetch karna [cite: 2025-12-23]"""
    try:
        random_page = random.randint(1, 100)
        url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient+birds&token={FREESOUND_API_KEY}&filter=duration:[10 TO 60]&fields=id,previews&page={random_page}"
        resp = requests.get(url, timeout=12).json()
        results = resp.get('results', [])
        if results:
            music_url = random.choice(results)['previews']['preview-hq-mp3']
            r = requests.get(music_url, timeout=20)
            with open("bg_music.mp3", "wb") as f: f.write(r.content)
            if os.path.getsize("bg_music.mp3") > 5000: return "bg_music.mp3"
    except: return None

def merge_video_audio(v_path, m_path, out_path):
    """Compulsory Merging Step: Pehle merge hoga tabhi aage badhega"""
    try:
        video = mp.VideoFileClip(v_path)
        audio = mp.AudioFileClip(m_path)

        # Audio ko video ki length ke hisaab se adjust karna [cite: 2025-12-23]
        if audio.duration < video.duration:
            audio = audio_loop(audio, duration=video.duration)
        else:
            audio = audio.set_duration(video.duration)

        # Mixing Audio into Video
        final_video = video.set_audio(audio.volumex(1.4))
        
        # Physical file export (is ke bina send nahi hoga)
        final_video.write_videofile(out_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True, fps=24, logger=None)
        
        video.close()
        audio.close()
        return out_path
    except Exception as e:
        print(f"Merging Failed: {e}")
        return None

def run_automation():
    # 1. Topic & History Setup
    topic = random.choice(STRICT_TOPICS)
    history_file = 'posted_videos.txt'
    if not os.path.exists(history_file): open(history_file, 'w').close()
    with open(history_file, 'r') as f: posted_ids = f.read().splitlines()

    # 2. Pexels Video Fetch
    url = f"https://api.pexels.com/videos/search?query={topic}&per_page=80&orientation=portrait"
    v_resp = requests.get(url, headers={"Authorization": PEXELS_API_KEY}).json()
    videos = v_resp.get('videos', [])
    random.shuffle(videos)

    for vid in videos:
        if str(vid['id']) not in posted_ids and 5 <= vid.get('duration', 0) <= 10:
            v_files = vid.get('video_files', [])
            best_v_url = next((f['link'] for f in v_files if 720 <= f['width'] <= 1920), v_files[0]['link'])

            # Video Download
            with open("raw_video.mp4", 'wb') as f: f.write(requests.get(best_v_url).content)
            
            # 3. Dynamic Music Download [cite: 2025-12-23]
            music_file = get_dynamic_music()
            
            if music_file:
                # 4. COMPULSORY MERGING (Important Part)
                final_merged_file = "final_ready.mp4"
                processed_video = merge_video_audio("raw_video.mp4", music_file, final_merged_file)
                
                # Check: Agar merge ho gaya tabhi Telegram aur Make.com ko send karega
                if processed_video and os.path.exists(processed_video):
                    title = random.choice(DYNAMIC_TITLES)[:15]
                    caption = random.choice(DYNAMIC_CAPTIONS)[:15]
                    full_desc = f"🎬 {title}\n\n{caption}\n\n{HASHTAGS}"

                    # 5. Telegram Post
                    with open(processed_video, 'rb') as v:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": full_desc}, files={"video": v})
                    
                    # 6. Make.com Webhook Post
                    if MAKE_WEBHOOK_URL:
                        requests.post(MAKE_WEBHOOK_URL, json={"title": title, "video_url": best_v_url, "caption": full_desc})

                    # 7. History Update
                    with open(history_file, 'a') as f: f.write(str(vid['id']) + '\n')
                    print(f"Post Completed: {title}")
                    return

if __name__ == "__main__":
    run_automation()
