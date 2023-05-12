import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from tenacity import RetryError

import tts
from explainer import retrieve_text_explanation


def display_header() -> None:
    st.title("Text Summarizer")
    st.text("Upload your text or copy and paste in the field below")

def display_widgets() -> tuple[UploadedFile, str]:
    file = st.file_uploader("Upload your text here.")
    text = st.text_area("Or copy and paste your text here (press Ctrl + Enter to send)")
    return file, text

def retrieve_content_from_file(file: UploadedFile) -> str:
    return file.getvalue().decode("utf8")

def extract_text() -> str:
    uploaded_text, pasted_text = display_widgets()
    if uploaded_text:
        return retrieve_content_from_file(uploaded_text)
    return pasted_text or ""

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
                st.warning("Couldn't access AI. Proceeding to text-to-speech")
                explanation = text_to_explain
                summary_worked = False
        with st.spinner(text="Converting to audio..."):
            tts.convert_text_to_mp3(
                message=explanation,
                voice_name=choose_voice(),
                mp3_filename=audio_file_name,
            )
        if summary_worked:
            st.success("Here's a summary of your text")
        else:
            st.warning("Summarizer might be offline")
        st.markdown(f"**Explanation:** {explanation}")
        st.audio(audio_file_name)


if __name__ == "__main__":
    main()