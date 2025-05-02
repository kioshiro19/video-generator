import os
import requests
from gtts import gTTS
from moviepy.editor import *
import json

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_script():
    prompt = {
        "contents": [{
            "parts": [{"text": "Crea un guion motivacional de 3 minutos para un video de YouTube"}]
        }]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        headers=headers,
        json=prompt
    )
    return response.json()['candidates'][0]['content']['parts'][0]['text']

def search_images(query):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 10}
    response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
    photos = response.json().get("photos", [])
    os.makedirs("assets/images", exist_ok=True)
    for idx, photo in enumerate(photos):
        img_url = photo["src"]["large"]
        img_data = requests.get(img_url).content
        with open(f"assets/images/image{idx}.jpg", "wb") as f:
            f.write(img_data)

def generate_voiceover(text):
    tts = gTTS(text)
    tts.save("assets/voice.mp3")

def generate_subtitles(text):
    lines = text.split(". ")
    subs = ""
    for i, line in enumerate(lines):
        start = f"00:00:{i*5:02d},000"
        end = f"00:00:{(i+1)*5:02d},000"
        subs += f"{i+1}\n{start} --> {end}\n{line.strip()}\n\n"
    with open("assets/subtitles.srt", "w") as f:
        f.write(subs)

def create_video():
    images = [ImageClip(f"assets/images/{img}")
              .set_duration(5) for img in sorted(os.listdir("assets/images"))]
    audio = AudioFileClip("assets/voice.mp3")
    video = concatenate_videoclips(images, method="compose").set_audio(audio)
    video.write_videofile("output_video.mp4", fps=24)

def main():
    script = generate_script()
    search_images("motivación")
    generate_voiceover(script)
    generate_subtitles(script)
    create_video()

if __name__ == "__main__":
    main()
