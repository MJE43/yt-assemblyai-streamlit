import streamlit as st
import yt_dlp as yt
import assemblyai as aai
from configure import auth_key

# Set API key for AssemblyAI
aai.settings.api_key = auth_key

# Decorator for caching data
@st.cache_data(ttl="1h", persist="disk", show_spinner=True)
def transcribe_audio(youtube_url, speaker_labels=False, speakers_expected=None):
    with yt.YoutubeDL() as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        # Safely extract audio URL using .get() to avoid KeyError
        audio_url = next((f["url"] for f in info["formats"] if f.get('acodec') != "none" and f["ext"] == "m4a"), None)

    if not audio_url:
        raise ValueError("No suitable audio format found.")
    
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(speaker_labels=speaker_labels, speakers_expected=speakers_expected)
    transcript = transcriber.transcribe(audio_url, config)

    if speaker_labels:
        return {"utterances": [{"speaker": utterance.speaker, "text": utterance.text} for utterance in transcript.utterances]}
    else:
        return {"text": transcript.text}

st.set_page_config(page_title="YouTube Transcription App")
st.title("YouTube Transcription App")

with st.form("youtube_url_form"):
    st.subheader("Enter YouTube URL")
    youtube_url = st.text_input("YouTube URL", placeholder="Enter the YouTube URL")
    speaker_labels = st.checkbox("Enable Speaker Diarization")
    speakers_expected = st.number_input("Number of Speakers (optional)", min_value=1, step=1)
    submit_button = st.form_submit_button("Transcribe")

if submit_button and youtube_url:
    try:
        st.video(youtube_url)
        with st.spinner('Transcribing audio... Please wait.'):
            transcript_data = transcribe_audio(youtube_url, speaker_labels, speakers_expected)
        st.session_state.transcript_data = transcript_data
    except Exception as e:
        st.error(f"Error: {e}")

if "transcript_data" in st.session_state:
    st.subheader("Video Transcript")
    if "utterances" in st.session_state.transcript_data:
        for utterance in st.session_state.transcript_data['utterances']:
            st.write(f"Speaker {utterance['speaker']}: {utterance['text']}")
        download_data = "\n".join(f"Speaker {utterance['speaker']}: {utterance['text']}" for utterance in st.session_state.transcript_data['utterances'])
    else:
        st.markdown(st.session_state.transcript_data['text'])
        download_data = st.session_state.transcript_data['text']
    st.download_button("Download Transcript", download_data, file_name="transcript.txt", mime="text/plain")
