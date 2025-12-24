import requests
import random
import os
import moviepy.editor as mp
from moviepy.audio.fx.all import audio_loop

# API Keys from GitHub Secrets
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
FREESOUND_API_KEY = os.getenv('FREESOUND_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

# Strict Pure Nature Topics (No Man-made objects, Max 10s)
STRICT_TOPICS = [
    "wild forest", "green hills", "pure river", "deep jungle", 
    "grassland", "wildflowers", "mossy rocks", "alpine peaks"
]

def get_dynamic_music():
    """Freesound se naya nature music select karna [cite: 2025-12-23]"""
    random_page = random.randint(1, 25)
    url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient&token={FREESOUND_API_KEY}&filter=duration:[10 TO 60]&fields=id,previews&page={random_page}"
    try:
        resp = requests.get(url).json()
        results = resp.get('results', [])
        if results:
            sound = random.choice(results)
            music_url = sound['previews']['preview-hq-mp3']
            with open("dynamic_music.mp3", "wb") as f:
                f.write(requests.get(music_url).content)
            return "dynamic_music.mp3"
    except Exception: return None

def add_bg_music(video_path, music_path, output_path):
    """Audio merge aur duration control"""
    try:
        video = mp.VideoFileClip(video_path)
        audio = mp.AudioFileClip(music_path)
        if audio.duration < video.duration:
            audio = audio_loop(audio, duration=video.duration)
        else:
            audio = audio.set_duration(video.duration)
        final_video = video.set_audio(audio)
        # Full HD Quality
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30, logger=None)
        video.close()
        audio.close()
        return output_path
    except Exception: return video_path

def run_automation():
    topic = random.choice(STRICT_TOPICS)
    url = f"https://api.pexels.com/videos/search?query={topic}&per_page=50&orientation=portrait"
    v_resp = requests.get(url, headers={"Authorization": PEXELS_API_KEY}).json()
    
    if not os.path.exists('posted_videos.txt'): open('posted_videos.txt', 'w').close()
    with open('posted_videos.txt', 'r') as f: posted_ids = f.read().splitlines()

    videos = v_resp.get('videos', [])
    random.shuffle(videos)

    for vid in videos:
        # Rules: No Repeat, Duration 5-10s, HD Quality
        if str(vid['id']) not in posted_ids and 5 <= vid.get('duration', 0) <= 10:
            video_files = vid.get('video_files', [])
            hd_file = next((f['link'] for f in video_files if f['width'] >= 1080), video_files[0]['link'])

            with open("temp.mp4", 'wb') as f: f.write(requests.get(hd_file).content)
            music_file = get_dynamic_music()
            
            if music_file:
                processed_file = add_bg_music("temp.mp4", music_file, "final.mp4")
                
                # Dynamic Title & Caption (Strictly Max 15 Characters)
                titles = ["Pure Nature", "Wild Green", "Fresh Vibes", "Quiet Forest", "Deep Valley", "Nature Magic"]
                captions = ["Feel the peace", "Green escape", "Pure beauty", "Nature love", "Wild & Free"]
                
                final_title = random.choice(titles)[:15]
                final_caption_text = random.choice(captions)[:15]
                
                # 8 Hashtags remain same
                full_description = f"🎬 {final_title}\n\n{final_caption_text}\n\n#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"

                # Deliveries
                with open(processed_file, 'rb') as v:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "caption": full_description}, files={"video": v})
                
                if MAKE_WEBHOOK_URL:
                    requests.post(MAKE_WEBHOOK_URL, json={"title": final_title, "caption": full_description, "video_url": hd_file})
                
                with open('posted_videos.txt', 'a') as f: f.write(str(vid['id']) + '\n')
                return

if __name__ == "__main__":
    run_automation()
