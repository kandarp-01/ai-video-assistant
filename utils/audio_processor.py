import yt_dlp
from pydub import AudioSegment
import os 
DOWNLOAD_DIR='downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok=True)
import uuid

def download_youtube_audio(url: str) -> str:

    output_path = os.path.join(
        DOWNLOAD_DIR,
        f"{uuid.uuid4()}_%(title)s.%(ext)s"
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,

        # JavaScript challenge support
        "js_runtimes": {
            "deno": {}
        },

        "remote_components": ["ejs:github"],

        # Audio conversion
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
            "preferredquality": "192",
        }],

        "noplaylist": True,
        "quiet": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        filename = ydl.prepare_filename(info)

        audio_path = os.path.splitext(filename)[0] + ".wav"

    if not os.path.exists(audio_path):
        raise FileNotFoundError(
            f"Converted audio file not found: {audio_path}"
        )

    return audio_path


def convert_to_wav(input_path:str)-> str:
    output_path = os.path.splitext(input_path)[0] + '_converted.wav'
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format='wav')
    return output_path



def chunk_audio(wav_path:str, chunk_minutes:int=10)-> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_length_ms = chunk_minutes * 60 * 1000  # Convert minutes to milliseconds
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_length_ms)):
        chunk = audio[start:start + chunk_length_ms]
        chunk_path=f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format='wav')
        chunks.append(chunk_path)
    return chunks

def process_youtube_audio(url: str) -> list:

    if url.startswith(("http://", "https://")):
        audio_path = download_youtube_audio(url)
    else:
        audio_path = convert_to_wav(url)

    chunks = chunk_audio(audio_path)
    return chunks

