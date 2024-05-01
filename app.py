import streamlit as st
import yt_dlp as yt_dlp
import assemblyai as aai
from configure import auth_key

@st.cache_data
def transcribe_audio(youtube_url):
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
    return transcript.text

st.set_page_config(page_title="YouTube Transcription App")

with st.form("youtube_url_form"):
    st.subheader("Enter YouTube URL")
    youtube_url = st.text_input("YouTube URL", placeholder="Enter the YouTube URL")
    submit_button = st.form_submit_button("Transcribe")

if submit_button:
    try:
        transcript = transcribe_audio(youtube_url)
        st.subheader("Video Transcript")
        st.markdown(transcript)
        st.download_button(
            label="Download Transcript",
            data=transcript,
            file_name="transcript.txt",
            mime="text/plain",
        )
    except Exception as e:
        st.error(f"Error: {e}")
