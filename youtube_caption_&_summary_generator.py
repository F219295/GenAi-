# -*- coding: utf-8 -*-
"""YouTube Caption & Summary Generator.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11o_8QJ4K_lu9R9uT3TnADQZLWNb7VrXQ
"""

!pip install yt-dlp openai-whisper gradio transformers
!sudo apt update && sudo apt install -y ffmpeg

import yt_dlp
import whisper
import gradio as gr
import os
from transformers import pipeline

# Load Whisper Model (Choose "base", "small", "medium", "large" as needed)
whisper_model = whisper.load_model("base")

# Load Summarization Model
summarizer = pipeline("summarization")

# Output directory for subtitles
os.makedirs("subtitles", exist_ok=True)

def download_audio(youtube_url):
    """Download audio from YouTube and return the file path."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "downloaded_audio.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return "downloaded_audio.mp3"

def transcribe_audio(youtube_url):
    """Fetch YouTube audio, transcribe it using Whisper AI, and generate subtitles."""
    audio_file = download_audio(youtube_url)

    # Transcribe using Whisper AI
    transcription = whisper_model.transcribe(audio_file)
    subtitles_text = transcription["text"]

    # Save subtitles in .srt and .txt format
    srt_file = "subtitles/output.srt"
    txt_file = "subtitles/output.txt"

    with open(srt_file, "w") as srt_f, open(txt_file, "w") as txt_f:
        srt_f.write(subtitles_text)
        txt_f.write(subtitles_text)

    return subtitles_text, srt_file, txt_file

def summarize_text(subtitles):
    """Summarize the transcribed subtitles."""
    summary = summarizer(subtitles, max_length=150, min_length=50, do_sample=False)
    return summary[0]["summary_text"]

# Custom CSS for UI Enhancements
custom_css = """
h1 {
    text-align: center;
    font-size: 36px;
    color: #ffffff;
    background: linear-gradient(90deg, #4A90E2, #9013FE);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 30px;
}

body {
    background-color: #f5f5f5;
    margin: 0;
    padding: 20px;
}

#component-0 {
    text-align: center;
}

#input_box {
    width: 100%;
    padding: 20px;
    font-size: 20px;
    border: 2px solid #9013FE;
    border-radius: 10px;
    margin-bottom: 20px;
}

.gradio-container {
    width: 80%;
    max-width: 1200px;
    background: white;
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    text-align: center;
    margin: 5% auto 0 auto;
}

gr.Textbox, gr.Button, gr.File {
    margin-bottom: 20px;
}

.button-container {
    display: flex;
    justify-content: center;
    gap: 20px;
}

#transcribe_btn, #summarize_btn {
    width: 40%;
    padding: 12px;
    font-size: 18px;
    background: linear-gradient(90deg, #ff5733, #ff8d1a);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.3s;
}

#transcribe_btn:hover, #summarize_btn:hover {
    background: linear-gradient(90deg, #ff8d1a, #ff5733);
}
"""

ui = gr.Blocks(css=custom_css)

with ui:
    gr.Markdown("# 🎬 YouTube Caption Generator")
    gr.Markdown("🎙️ **Enter a YouTube video URL to generate subtitles and summary.**")

    with gr.Row():
        youtube_link = gr.Textbox(placeholder="🔗 Paste YouTube Video URL Here", label="YouTube URL", elem_id="input_box")

    with gr.Row(elem_id="button-container"):
        transcribe_button = gr.Button("🎧 Transcribe Audio", elem_id="transcribe_btn")
        summarize_button = gr.Button("📝 Summarize Subtitles", elem_id="summarize_btn")

    subtitle_output = gr.Textbox(label="Generated Subtitles", lines=10)
    summary_output = gr.Textbox(label="Summary", lines=5)
    download_srt = gr.File(label="Download Subtitles (.srt)")
    download_txt = gr.File(label="Download Subtitles (.txt)")

    transcribe_button.click(transcribe_audio, inputs=[youtube_link], outputs=[subtitle_output, download_srt, download_txt])
    summarize_button.click(summarize_text, inputs=[subtitle_output], outputs=[summary_output])

ui.launch()