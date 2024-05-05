import streamlit as st
import yt_dlp as yt_dlp
import assemblyai as aai
from configure import auth_key

@st.cache_data
def transcribe_audio(youtube_url, speaker_labels=False, speakers_expected=None):
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        for format in info["formats"][::-1]:
            if format["resolution"] == "audio only" and format["ext"] == "m4a":
                url = format["url"]
                break

    aai.settings.api_key = auth_key
    transcriber = aai.Transcriber()
    config = aai.TranscriptionConfig(
        speaker_labels=speaker_labels,
        speakers_expected=speakers_expected
    )
    transcript = transcriber.transcribe(url, config)

    # Convert the Transcript object to a dictionary for serialization
    if speaker_labels:
        transcript_data = {
            "utterances": [{"speaker": utterance.speaker, "text": utterance.text} for utterance in transcript.utterances]
        }
    else:
        transcript_data = {"text": transcript.text}
    
    return transcript_data

st.set_page_config(page_title="YouTube Transcription App")

st.title("YouTube Transcription App")

with st.form("youtube_url_form"):
    st.subheader("Enter YouTube URL")
    youtube_url = st.text_input("YouTube URL", placeholder="Enter the YouTube URL")
    speaker_labels = st.checkbox("Enable Speaker Diarization")
    speakers_expected = st.number_input("Number of Speakers (optional)", min_value=1, step=1)
    submit_button = st.form_submit_button("Transcribe")

if submit_button:
    if not youtube_url:
        st.warning("Please enter a YouTube URL.")
    else:
        try:
            # Embed the YouTube video
            st.video(youtube_url)

            with st.spinner('Transcribing audio... Please wait.'):
                transcript_data = transcribe_audio(youtube_url, speaker_labels, speakers_expected)
            
            # Store the transcript data in session state
            st.session_state.transcript_data = transcript_data

        except Exception as e:
            st.error(f"Error: {e}")

# Display the transcript if it exists in the session state
if "transcript_data" in st.session_state:
    st.subheader("Video Transcript")
    if isinstance(st.session_state.transcript_data, dict) and "utterances" in st.session_state.transcript_data:
        for utterance in st.session_state.transcript_data['utterances']:
            st.write(f"Speaker {utterance['speaker']}: {utterance['text']}")
        # Prepare data for download
        download_data = "\n".join(f"Speaker {utterance['speaker']}: {utterance['text']}" for utterance in st.session_state.transcript_data['utterances'])
    else:
        st.markdown(st.session_state.transcript_data['text'])
        download_data = st.session_state.transcript_data['text']
    
    st.download_button(
        label="Download Transcript",
        data=download_data,
        file_name="transcript.txt",
        mime="text/plain",
    )
