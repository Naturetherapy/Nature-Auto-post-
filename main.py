import requests
import random
import os

# API Configurations (GitHub Secrets se aayenge)
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
MAKE_WEBHOOK_URL = os.getenv('MAKE_WEBHOOK_URL')

def get_nature_image():
    # Pexels se nature image search karna
    url = "https://api.pexels.com/v1/search?query=nature&per_page=50"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers).json()
    
    # Randomly ek photo select karna
    image = random.choice(response['photos'])
    img_url = image['src']['large']
    img_title = image['alt'] if image['alt'] else "Beautiful Nature"
    return img_url, img_title

def post_to_telegram(img_url, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    data = {"chat_id": TELEGRAM_CHAT_ID, "photo": img_url, "caption": caption}
    requests.post(url, data=data)
    print("Sent to Telegram")

def post_to_make_webhook(img_url, title, caption):
    # Make.com ko data bhejna
    payload = {
        "image_url": img_url,
        "title": title,
        "caption": caption
    }
    requests.post(MAKE_WEBHOOK_URL, json=payload)
    print("Sent to Make.com Webhook")

if __name__ == "__main__":
    image_url, title = get_nature_image()
    
    # Automated Caption and Hashtags
    full_caption = f"🌿 {title}\n\nNature's beauty at its best! ✨\n\n#nature #photography #greenery #earth #naturelovers"
    
    # Dono platforms par post karein
    post_to_telegram(image_url, full_caption)
    post_to_make_webhook(image_url, title, full_caption)
