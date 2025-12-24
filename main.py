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

# Strict Pure Nature Topics (No Man-made objects)
STRICT_TOPICS = [
    "wild green forest no people", "lush green mountain landscape", 
    "natural valley river", "deep rainforest plants", "green grassland wind", 
    "wildflower meadow close up", "forest floor moss flowers", 
    "riverbank vegetation nature", "alpine flowers mountains", "seasonal wildflowers field"
]

def generate_dynamic_title(topic):
    """Exactly 50 characters ka dynamic title generate karna"""
    prefixes = ["Amazing View of", "Pure Nature:", "Beautiful", "Peaceful", "Wonderful", "Explore the"]
    suffixes = ["Vibes ✨", "in 4K 🌿", "Serenity Now", "Natural Beauty", "Magic 🍃"]
    
    title = f"{random.choice(prefixes)} {topic.replace(' no people', '').title()} {random.choice(suffixes)}"
    # Title ko exactly 50 characters ka banana
    return title[:47].ljust(50, '.') if len(title) > 50 else title.ljust(50, ' ')

def get_dynamic_music():
    """Freesound se naya nature music select karna [cite: 2025-12-23]"""
    random_page = random.randint(1, 20)
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
            audio = audio.set_audio(audio).set_duration(video.duration)
            
        final_video = video.set_audio(audio)
        # Full HD Quality
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=30)
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
        # Rules: No Repeat, Max 10s, HD Quality
        if str(vid['id']) not in posted_ids and 5 <= vid.get('duration', 0) <= 10:
            video_files = vid.get('video_files', [])
            hd_file = next((f['link'] for f in video_files if f['width'] >= 1080), video_files[0]['link'])

            with open("temp.mp4", 'wb') as f: f.write(requests.get(hd_file).content)
            music_file = get_dynamic_music()
            
            if music_file:
                processed_file = add_bg_music("temp.mp4", music_file, "final.mp4")
                
                # Dynamic Title & Caption
                title = generate_dynamic_title(topic)
                caption_texts = [
                    "Experience the calmness of nature.",
                    "A short escape into the wild.",
                    "Soothing greenery for your soul.",
                    "Nature's beauty in every second."
                ]
                dynamic_caption = f"🎬 {title}\n\n{random.choice(caption_texts)}\n\n#nature #greenery #wildlife #forest #flowers #mountains #serenity #naturephotography"

                # Deliveries
                with open(processed_file, 'rb') as v:
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo", 
                                  data={"chat_id": TELEGRAM_CHAT_ID, "caption": dynamic_caption}, files={"video": v})
                
                if MAKE_WEBHOOK_URL:
                    requests.post(MAKE_WEBHOOK_URL, json={"title": title, "caption": dynamic_caption, "video_url": hd_file})
                
                with open('posted_videos.txt', 'a') as f: f.write(str(vid['id']) + '\n')
                return

if __name__ == "__main__":
    run_automation()
