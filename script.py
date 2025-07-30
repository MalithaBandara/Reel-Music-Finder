import json
import yt_dlp
import ffmpeg
import imageio_ffmpeg as iio_ffmpeg
import asyncio
import json
from shazamio import Shazam

with open('JSON/input.json', 'r') as file:
    data = json.load(file)

link = data['link']

ydl_opts = {
    'format': 'best',            
    'outtmpl': 'media/video.%(ext)s',
    'quiet': False,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([link])

inpt = "media/video.mp4"
outpt = "media/audio.mp3"

ffmpeg_binary = iio_ffmpeg.get_ffmpeg_exe()

ffmpeg.input(inpt).output(outpt).run(cmd=ffmpeg_binary)

async def main():
    shazam = Shazam()
    out = await shazam.recognize('media/audio.mp3')

    track = out['track']
    hub = track.get('hub', {})

    spotify = None
    yt_music = None
    apple = None

    for action in hub.get("actions", []):
        if action.get("type") == "uri":
            apple = action.get("uri")
            break

    for provider in hub.get("providers", []):
        if provider.get("type") == "SPOTIFY":
            for action in provider.get("actions", []):
                if action.get("type") == "uri":
                    spotify = action.get("uri")
                    break
        elif provider.get("type") == "YOUTUBEMUSIC":
            for action in provider.get("actions", []):
                if action.get("type") == "uri":
                    yt_music = action.get("uri")
                    break

    result = {
        "name": track.get("title"),
        "artist": track.get("subtitle"),
        "cover": track.get("images", {}).get("coverart"),
        "spotify": spotify,
        "apple_music": apple,
        "yt_music": yt_music
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    with open("JSON/output.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

asyncio.run(main())
