import requests
import random
import os
import moviepy.editor as mp
from moviepy.audio.fx.all import audio_loop

# API Keys aur Webhook
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
FREESOUND_API_KEY = os.getenv('FREESOUND_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Insaan aur Sadak hatane ke liye ultra-strict topics
STRICT_TOPICS = [
    "forest nature no people", "moving clouds mountain top", 
    "deep jungle river wilderness", "wild grass wind nature", 
    "unspoiled waterfall forest", "dense greenery background"
]

def get_dynamic_music():
    """Freesound se verified nature music download karna [cite: 2025-12-23]"""
    r_page = random.randint(1, 50)
    url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient+birds&token={FREESOUND_API_KEY}&filter=duration:[10 TO 60]&fields=id,previews&page={r_page}"
    try:
        resp = requests.get(url, timeout=10).json()
        results = resp.get('results', [])
        if results:
            music_url = random.choice(results)['previews']['preview-hq-mp3']
            r = requests.get(music_url, timeout=15)
            with open("bg_music.mp3", "wb") as f:
                f.write(r.content)
            # Check if file is valid size to avoid OSError
            if os.path.getsize("bg_music.mp3") > 5000:
                return "bg_music.mp3"
    except Exception: return None

def add_bg_music(video_path, music_path, output_path):
    """Audio ko loop karke video mein merge karna"""
    try:
        video = mp.VideoFileClip(video_path)
        if not music_path: return None
        
        audio = mp.AudioFileClip(music_path)
        if audio.duration < video.duration:
            audio = audio_loop(audio, duration=video.duration)
        else:
            audio = audio.set_duration(video.duration)
            
        # Nature music ka volume thoda loud rakha hai [cite: 2025-12-23]
        final_video = video.set_audio(audio.volumex(1.3))
        # Medium HD Quality (720p/1080p)
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True, fps=24, logger=None)
        
        video.close()
        audio.close()
        return output_path
    except Exception: return None

def run_automation():
    topic = random.choice(STRICT_TOPICS)
    url = f"https://api.pexels.com/videos/search?query={topic}&per_page=50&orientation=portrait"
    v_resp = requests.get(url, headers={"Authorization": PEXELS_API_KEY}).json()
    
    if not os.path.exists('posted_videos.txt'): open('posted_videos.txt', 'w').close()
    with open('posted_videos.txt', 'r') as f: posted_ids = f.read().splitlines()

    videos = v_resp.get('videos', [])
    random.shuffle(videos)

    for vid in videos:
        # Rules: No Repeat, Max 10s, Pure Nature only
        if str(vid['id']) not in posted_ids and 5 <= vid.get('duration', 0) <= 10:
            v_files = vid.get('video_files', [])
            # Mobile ke liye HD link select karna
            best_v = next((f['link'] for f in v_files if 720 <= f['width'] <= 1920), v_files[0]['link'])

            with open("temp.mp4", 'wb') as f: f.write(requests.get(best_v).content)
            
            music = get_dynamic_music()
            if music:
                final_file = add_bg_music("temp.mp4", music, "final_nature.mp4")
                if final_file:
                    # Title/Caption: Strictly Max 15 letters
                    title = "Pure Nature"[:15]
                    caption = "Green Magic"[:15]
                    tags = "#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"
                    full_desc = f"🎬 {title}\n\n{caption}\n\n{tags}"

                    # Post to Telegram
                    with open(final_file, 'rb') as v:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": full_desc}, files={"video": v})
                    
                    # Send to Make.com Webhook
                    if MAKE_WEBHOOK_URL:
                        requests.post(MAKE_WEBHOOK_URL, json={"title": title, "video_url": best_v, "caption": full_desc})

                    with open('posted_videos.txt', 'a') as f: f.write(str(vid['id']) + '\n')
                    return

if __name__ == "__main__":
    run_automation()
