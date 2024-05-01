import streamlit as st
import yt_dlp as yt_dlp
import assemblyai as aai
from configure import auth_key

with st.form("youtube_url_form"):
    youtube_url = st.text_input("Enter the YouTube URL:")
    submit_button = st.form_submit_button("Submit")

if submit_button:
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(youtube_url, download=False)

    # formats are already sorted worst to best
    # --> iterate in reverse and take the first audio to get the best
    for format in info["formats"][::-1]:
        if format["resolution"] == "audio only" and format["ext"] == "m4a":
            url = format["url"]
            break

    aai.settings.api_key = auth_key

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(url)

    with st.expander("Video Transcript"):
        st.write(transcript.text)