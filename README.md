# AI Video Assistant

AI Video Assistant is a Streamlit application that turns YouTube videos or local audio/video files into structured video intelligence. It transcribes media, generates an executive summary, extracts action items and decisions, identifies open questions, and provides transcript-grounded chat through Retrieval Augmented Generation (RAG).

The interface is branded as **VidzAI** in the application.

## Features

- Accepts YouTube URLs or local MP3, WAV, MP4, M4A, WEBM, and OGG files
- Supports English and Hinglish transcription modes
- Uses local OpenAI Whisper transcription for English content
- Uses the Sarvam STT-Translate API for Hinglish content
- Generates a concise video title and professional summary
- Extracts action items, owners, deadlines, key decisions, and open questions
- Builds a local Chroma vector database for context-aware question answering
- Provides suggested prompts and conversational chat in the Streamlit UI
- Displays the full transcript and downloads it as a text file
- Includes separate CLI and Streamlit workflows

## How It Works

```text
YouTube URL or local media
        |
        v
Audio download / conversion
        |
        v
10-minute audio chunks
        |
        v
Whisper or Sarvam transcription
        |
        v
Groq-hosted Qwen model analysis
        |
        v
Title, summary, actions, decisions, questions
        |
        v
Chroma embeddings + RAG chat
```

The RAG knowledge base uses Sentence Transformers embeddings with Chroma. For each processed transcript, text is split into smaller chunks and indexed locally in `vector_db/`.

## Technology Stack

- Python 3.10+
- Streamlit
- OpenAI Whisper
- Sarvam STT-Translate API
- Groq and LangChain
- ChromaDB
- Hugging Face Sentence Transformers
- yt-dlp and FFmpeg
- pydub

## Prerequisites

- Python 3.10 or newer
- FFmpeg available on the system `PATH`
- A Groq API key
- A Sarvam API key if Hinglish transcription will be used
- Enough local disk space and memory for the selected Whisper model

### macOS

```bash
brew install ffmpeg
```

### Ubuntu or Debian

```bash
sudo apt update
sudo apt install ffmpeg
```

## Installation

1. Clone the repository and enter the project directory:

```bash
git clone <your-repository-url>
cd ai-video-assistant
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Install the Python dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```dotenv
GROQ_API_KEY=gsk_your_groq_api_key
SARVAM_API_KEY=your_sarvam_api_key
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
```

- `GROQ_API_KEY` is used for summaries, title generation, extraction, and RAG answers.
- `SARVAM_API_KEY` is required only for Hinglish transcription.
- `WHISPER_MODEL` controls the local Whisper model and defaults to `small`.
- `SARVAM_STT_MODEL` defaults to `saaras:v2.5`.

Common Whisper model choices include `tiny`, `base`, `small`, `medium`, and `large`. Larger models improve transcription quality but require more memory and processing time.

## Running the Streamlit App

From the project root, run:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit, then:

1. Choose **YouTube URL** or **Local media file**.
2. Select **English** or **Hinglish**.
3. Generate the intelligence report.
4. Review the summary and extracted insights.
5. Open **AI Assistant** to ask questions about the transcript.

Downloaded YouTube audio and uploaded media files are stored under `downloads/`. The persistent Chroma data is stored under `vector_db/`.

## Running the CLI

The command-line pipeline is available through `main.py`:

```bash
python main.py
```

Enter a YouTube URL or local media path, then choose `english` or `hinglish`. The CLI prints the title, summary, action items, decisions, and open questions. It also starts an interactive RAG chat session; type `exit`, `quit`, or `q` to stop.

## Project Structure

```text
.
├── app.py                  # Streamlit web interface
├── main.py                 # CLI pipeline and interactive chat
├── requirements.txt        # Python dependencies
├── core/
│   ├── extractor.py        # Action items, decisions, and questions
│   ├── rag_engine.py       # RAG prompt chain and question answering
│   ├── summarize.py        # Title and summary generation
│   ├── transcriber.py      # Whisper and Sarvam transcription
│   └── vector_store.py     # Chroma vector store
├── utils/
│   └── audio_processor.py  # Download, conversion, and chunking
├── downloads/              # Downloaded and converted media
└── vector_db/              # Persistent Chroma data
```

## Processing Behavior

- YouTube audio is downloaded as WAV and stored in `downloads/`.
- Local media is converted to mono 16 kHz WAV before processing.
- Audio is divided into 10-minute chunks for transcription.
- Whisper handles English transcription locally.
- Hinglish audio is sent to Sarvam in 25-second pieces.
- The transcript is split and embedded for retrieval in Chroma.
- RAG answers are restricted to the retrieved transcript context.

## Troubleshooting

### `GROQ_API_KEY` is missing

Add `GROQ_API_KEY` to `.env` and restart the application.

### `SARVAM_API_KEY` is not set

The Hinglish option requires `SARVAM_API_KEY`. English transcription does not.

### FFmpeg was not found

Install FFmpeg and confirm it is available:

```bash
ffmpeg -version
```

### Whisper fails to load or runs slowly

Try a smaller model by setting `WHISPER_MODEL=tiny` or `base`. The initial model download may take several minutes.

### A YouTube download fails

Verify that the URL is publicly accessible and that `yt-dlp` is installed. Geographic restrictions, private videos, deleted videos, and membership-only content may not be downloadable.

## Generated Artifacts

The application creates and uses local files that should not contain sensitive content when committed to source control:

- `downloads/` - downloaded and processed media
- `vector_db/` - generated transcript embeddings
- `.env` - API credentials

## Limitations

- Transcription accuracy depends on media quality and the selected model.
- Long videos require significant time and memory.
- Chroma storage is currently shared by the application rather than separated per user.
- YouTube availability and download restrictions vary by region and publisher.
- API usage may incur provider costs or be subject to rate limits.
