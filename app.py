import streamlit as st
import yt_dlp as yt
import assemblyai as aai
from configure import auth_key

# Set API key for AssemblyAI
aai.settings.api_key = auth_key

# Function to extract audio URL from YouTube video
def extract_audio_url(youtube_url):
    with yt.YoutubeDL() as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        audio_url = next((f["url"] for f in info["formats"] if f.get('acodec') != "none" and f["ext"] == "m4a"), None)
    if not audio_url:
        raise ValueError("No suitable audio format found.")
    return audio_url

# Function to transcribe audio using AssemblyAI
def transcribe_audio(youtube_url, speaker_labels=False, speakers_expected=None):
    audio_url = extract_audio_url(youtube_url)
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(speaker_labels=speaker_labels, speakers_expected=speakers_expected)
    transcript = transcriber.transcribe(audio_url, config)
    if speaker_labels:
        return {"utterances": [{"speaker": utterance.speaker, "text": utterance.text} for utterance in transcript.utterances]}
    else:
        return {"text": transcript.text}

# Streamlit app configuration
st.set_page_config(page_title="YouTube Transcription App", layout="centered")
st.title("YouTube Transcription App")
st.write("Transcribe and download YouTube video transcripts easily.")

# Form to input YouTube URL and transcription options
with st.form("youtube_url_form"):
    st.subheader("Enter YouTube URL")
    youtube_url = st.text_area("YouTube URL", placeholder="Enter the YouTube URL", help="Paste the URL of the YouTube video you want to transcribe.")
    speaker_labels = st.checkbox("Enable Speaker Diarization", help="Identify and label different speakers in the transcript.")
    speakers_expected = st.number_input("Number of Speakers (optional)", min_value=1, step=1, help="Specify the number of speakers for better accuracy.")
    submit_button = st.form_submit_button("Transcribe")

# Display video if URL is provided
if youtube_url:
    st.video(youtube_url)

# Handle form submission
if submit_button and youtube_url:
    try:
        with st.spinner('Transcribing audio... Please wait.'):
            transcript_data = transcribe_audio(youtube_url, speaker_labels, speakers_expected)
        st.session_state.transcript_data = transcript_data
    except Exception as e:
        st.error(f"Error: {e}", icon="🚨")

# Display transcript if available
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