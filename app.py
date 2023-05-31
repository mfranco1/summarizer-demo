import streamlit as st
from tenacity import RetryError

import tts
from converter import speech_to_text
from explainer import retrieve_text_explanation
from st_custom_components import st_audiorec


def display_header() -> None:
    st.title("CAMS: Clinical Assistant Medical Scribe")
    st.text("Record your consultation session below")

def display_widgets() -> str:
    wav_audio_data = st_audiorec()
    if wav_audio_data is not None:
        return speech_to_text()
    return ""

def extract_text() -> str:
    return display_widgets()

def choose_voice():
    voices = tts.list_available_names()
    return voices[0]

def main() -> None:
    display_header()
    audio_file_name = "explanation.mp3"
    summary_worked = True
    if text_to_explain := extract_text():
        with st.spinner(text="Processing..."):
            try:
                explanation = retrieve_text_explanation(text=text_to_explain)
            except RetryError:
                st.warning("Couldn't access API. Proceeding to text-to-speech")
                explanation = text_to_explain
                summary_worked = False
        with st.spinner(text="Converting to audio..."):
            tts.convert_text_to_mp3(
                message=explanation,
                voice_name=choose_voice(),
                mp3_filename=audio_file_name,
            )
        if summary_worked:
            st.success("Here's a summary of your recording")
        else:
            st.warning("Summarizer might be offline")
        st.markdown(f"**Summary Report:** {explanation}")
        st.audio(audio_file_name)


if __name__ == "__main__":
    main()