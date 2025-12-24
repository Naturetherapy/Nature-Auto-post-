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

# Strict Pure Nature Filter (Man-made things hatane ke liye)
STRICT_TOPICS = [
    "nature landscape no people", "dense green forest wilderness", 
    "mountain river water", "unspoiled nature greenery", 
    "rainforest plants close up", "wildflower meadow field"
]

def get_dynamic_music():
    """Freesound se naya music fetch karna [cite: 2025-12-23]"""
    # Random page number taaki har baar naya music mile
    r_page = random.randint(1, 20)
    url = f"https://freesound.org/apiv2/search/text/?query=nature+ambient&token={FREESOUND_API_KEY}&filter=duration:[10 TO 60]&fields=id,previews&page={r_page}"
    try:
        resp = requests.get(url, timeout=10).json()
        results = resp.get('results', [])
        if results:
            music_url = random.choice(results)['previews']['preview-hq-mp3']
            r = requests.get(music_url, timeout=15)
            with open("dynamic_music.mp3", "wb") as f:
                f.write(r.content)
            return "dynamic_music.mp3"
    except Exception as e:
        print(f"Music Error: {e}")
    return None

def add_bg_music(video_path, music_path, output_path):
    """Audio looping logic taaki duration error na aaye"""
    try:
        video = mp.VideoFileClip(video_path)
        audio = mp.AudioFileClip(music_path)
        
        # Audio chhota ho toh loop karein
        if audio.duration < video.duration:
            audio = audio_loop(audio, duration=video.duration)
        else:
            audio = audio.set_duration(video.duration)
            
        final_video = video.set_audio(audio)
        # HD 1080p Export
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, logger=None)
        video.close()
        audio.close()
        return output_path
    except Exception as e:
        print(f"Edit Error: {e}")
        return video_path

def run_automation():
    topic = random.choice(STRICT_TOPICS)
    # Search for Pure Nature only (Portrait, HD)
    url = f"https://api.pexels.com/videos/search?query={topic}&per_page=50&orientation=portrait"
    v_resp = requests.get(url, headers={"Authorization": PEXELS_API_KEY}).json()
    
    if not os.path.exists('posted_videos.txt'): open('posted_videos.txt', 'w').close()
    with open('posted_videos.txt', 'r') as f: posted_ids = f.read().splitlines()

    videos = v_resp.get('videos', [])
    random.shuffle(videos)

    for vid in videos:
        # Check: No Repeat, Duration 5-10s, Pure Nature only
        if str(vid['id']) not in posted_ids and 5 <= vid.get('duration', 0) <= 10:
            
            # HD video select karna
            video_files = vid.get('video_files', [])
            hd_file = next((f['link'] for f in video_files if f['width'] >= 1080), video_files[0]['link'])

            # Download Video
            with open("temp.mp4", 'wb') as f:
                f.write(requests.get(hd_file).content)
            
            # Dynamic Music Process
            music_file = get_dynamic_music()
            if music_file:
                processed_file = add_bg_music("temp.mp4", music_file, "final.mp4")
                
                # Dynamic Title & Caption (Max 15 Characters)
                title = "Pure Nature"[:15]
                caption_text = "Green Magic"[:15]
                hashtags = "#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"
                
                full_caption = f"🎬 {title}\n\n{caption_text}\n\n{hashtags}"

                # Send to Telegram
                with open(processed_file, 'rb') as v:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "caption": full_caption}, files={"video": v})
                
                with open('posted_videos.txt', 'a') as f: f.write(str(vid['id']) + '\n')
                return

if __name__ == "__main__":
    run_automation()
