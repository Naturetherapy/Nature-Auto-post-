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

def get_dynamic_music():
    """Freesound se Nature Music fetch aur check karna [cite: 2025-12-23]"""
    r_page = random.randint(1, 50)
    # Nature ambient sounds like birds, wind, forest [cite: 2025-12-23]
    url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient+birds&token={FREESOUND_API_KEY}&filter=duration:[10 TO 60]&fields=id,previews&page={r_page}"
    try:
        resp = requests.get(url, timeout=10).json()
        results = resp.get('results', [])
        if results:
            music_url = random.choice(results)['previews']['preview-hq-mp3']
            r = requests.get(music_url, timeout=15)
            with open("bg_music.mp3", "wb") as f:
                f.write(r.content)
            # File size check taaki khali audio na ho
            if os.path.getsize("bg_music.mp3") > 2000:
                return "bg_music.mp3"
    except Exception as e:
        print(f"Music Download Fail: {e}")
    return None

def add_bg_music(video_path, music_path, output_path):
    """Video mein audio merge karna aur quality optimize karna"""
    try:
        video = mp.VideoFileClip(video_path)
        if not music_path or not os.path.exists(music_path):
            return None # Music nahi toh post nahi karenge

        audio = mp.AudioFileClip(music_path)
        
        # Audio ko loop ya cut karna video ke hisaab se
        if audio.duration < video.duration:
            audio = audio_loop(audio, duration=video.duration)
        else:
            audio = audio.set_duration(video.duration)
            
        # Nature sounds ko thoda loud rakha hai [cite: 2025-12-23]
        final_audio = audio.volumex(1.3)
        final_video = video.set_audio(final_audio)
        
        # Balanced High Quality (720p/1080p)
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True, fps=24, logger=None)
        
        video.close()
        audio.close()
        return output_path
    except Exception as e:
        print(f"Editing Error: {e}")
        return None

def run_automation():
    # Ultra-Strict Nature Search (No people/roads)
    TOPICS = ["forest stream aerial", "mountain mist nature", "deep jungle leaves", "wildflower meadow"]
    topic = random.choice(TOPICS)
    
    url = f"https://api.pexels.com/videos/search?query={topic}&per_page=40&orientation=portrait"
    v_resp = requests.get(url, headers={"Authorization": PEXELS_API_KEY}).json()
    
    if not os.path.exists('posted_videos.txt'): open('posted_videos.txt', 'w').close()
    with open('posted_videos.txt', 'r') as f: posted_ids = f.read().splitlines()

    videos = v_resp.get('videos', [])
    random.shuffle(videos)

    for vid in videos:
        # Rules: No Repeat, 5-10s, Pure Nature
        if str(vid['id']) not in posted_ids and 5 <= vid.get('duration', 0) <= 10:
            v_files = vid.get('video_files', [])
            # Medium-High HD quality select karna
            best_v = next((f['link'] for f in v_files if 720 <= f['width'] <= 1920), v_files[0]['link'])

            with open("temp.mp4", 'wb') as f:
                f.write(requests.get(best_v).content)
            
            music = get_dynamic_music()
            if music:
                final_file = add_bg_music("temp.mp4", music, "ready.mp4")
                
                if final_file:
                    # Dynamic Title/Caption: Max 15 letters
                    title = "Pure Nature"[:15]
                    caption = "Green Magic"[:15]
                    tags = "#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"
                    full_txt = f"🎬 {title}\n\n{caption}\n\n{tags}"

                    # Telegram Post
                    with open(final_file, 'rb') as v:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": full_txt}, files={"video": v})
                    
                    # Make.com Webhook
                    if MAKE_WEBHOOK_URL:
                        requests.post(MAKE_WEBHOOK_URL, json={"title": title, "video_url": best_v, "caption": full_txt})

                    with open('posted_videos.txt', 'a') as f: f.write(str(vid['id']) + '\n')
                    return

if __name__ == "__main__":
    run_automation()
