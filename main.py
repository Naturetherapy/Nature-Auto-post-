import requests
import random
import os
import moviepy.editor as mp
from moviepy.audio.fx.all import audio_loop

# API Keys
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
FREESOUND_API_KEY = os.getenv('FREESOUND_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

def get_dynamic_music():
    """Freesound se Nature Music download karna aur verify karna [cite: 2025-12-23]"""
    # Random page taaki music repeat na ho
    r_page = random.randint(1, 40)
    url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient+birds&token={FREESOUND_API_KEY}&filter=duration:[10 TO 60]&fields=id,previews&page={r_page}"
    try:
        resp = requests.get(url, timeout=10).json()
        results = resp.get('results', [])
        if results:
            music_url = random.choice(results)['previews']['preview-hq-mp3']
            r = requests.get(music_url, timeout=15)
            # Music file ko hamesha fresh overwrite karna
            with open("dynamic_music.mp3", "wb") as f:
                f.write(r.content)
            
            # Check if file is valid size
            if os.path.getsize("dynamic_music.mp3") > 1000:
                return "dynamic_music.mp3"
    except Exception as e:
        print(f"Music Download Error: {e}")
    return None

def add_bg_music(video_path, music_path, output_path):
    """Audio ko video mein pakka add karne ka logic"""
    try:
        video = mp.VideoFileClip(video_path)
        
        if music_path and os.path.exists(music_path):
            audio = mp.AudioFileClip(music_path)
            
            # Audio ko video ki length ke barabar set karna
            if audio.duration < video.duration:
                audio = audio_loop(audio, duration=video.duration)
            else:
                audio = audio.set_duration(video.duration)
            
            # Audio volume thoda badhana taaki saaf sunayi de
            final_audio = audio.volumex(1.2)
            final_video = video.set_audio(final_audio)
        else:
            # Agar music fail ho jaye toh bina music ke na bheje (skip karein)
            return None

        # Standard HD Quality (Na bahut zyada high, na low)
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True, fps=24, logger=None)
        
        video.close()
        audio.close()
        return output_path
    except Exception as e:
        print(f"Audio Addition Error: {e}")
        return None

def run_automation():
    # Pure Nature Topics Only
    STRICT_TOPICS = ["forest river no people", "mountain clouds nature", "jungle greenery", "wild grass wind"]
    topic = random.choice(STRICT_TOPICS)
    
    url = f"https://api.pexels.com/videos/search?query={topic}&per_page=40&orientation=portrait"
    v_resp = requests.get(url, headers={"Authorization": PEXELS_API_KEY}).json()
    
    if not os.path.exists('posted_videos.txt'): open('posted_videos.txt', 'w').close()
    with open('posted_videos.txt', 'r') as f: posted_ids = f.read().splitlines()

    videos = v_resp.get('videos', [])
    random.shuffle(videos)

    for vid in videos:
        # Rules: No Repeat, 5-10s Duration, HD
        if str(vid['id']) not in posted_ids and 5 <= vid.get('duration', 0) <= 10:
            v_files = vid.get('video_files', [])
            # Good quality link select karna (720p to 1080p)
            best_link = next((f['link'] for f in v_files if 720 <= f['width'] <= 1920), v_files[0]['link'])

            with open("temp.mp4", 'wb') as f:
                f.write(requests.get(best_link).content)
            
            music_file = get_dynamic_music()
            if music_file:
                processed_file = add_bg_music("temp.mp4", music_file, "final.mp4")
                
                if processed_file:
                    # Title/Caption: Max 15 letters
                    title = "Pure Nature"[:15]
                    caption_text = "Green Magic"[:15]
                    hashtags = "#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"
                    full_caption = f"🎬 {title}\n\n{caption_text}\n\n{hashtags}"

                    # Telegram Post
                    with open(processed_file, 'rb') as v:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                      data={"chat_id": TELEGRAM_CHAT_ID, "caption": full_caption}, files={"video": v})
                    
                    # Make.com Webhook
                    if MAKE_WEBHOOK_URL:
                        requests.post(MAKE_WEBHOOK_URL, json={"title": title, "video_url": best_link, "caption": full_caption})

                    with open('posted_videos.txt', 'a') as f: f.write(str(vid['id']) + '\n')
                    return

if __name__ == "__main__":
    run_automation()
