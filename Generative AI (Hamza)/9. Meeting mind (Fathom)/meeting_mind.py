import streamlit as st
import google.generativeai as genai
import os
import time

# --- CONFIGURATION ---
# Replace with your actual key or use environment variable
os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    # Check if the file is ready to be used
    while file.state.name == "PROCESSING":
        time.sleep(2)
        file = genai.get_file(file.name)
    return file


# --- UI LAYOUT ---
st.set_page_config(page_title="MeetingMind", page_icon="🧠")
st.title("🧠 MeetingMind: AI Meeting Assistant")
st.markdown("Upload a meeting recording (MP3/WAV) to get a **Fathom-style summary** and **Action Items**.")

# 1. File Upload
uploaded_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    # Save file temporarily to disk (Gemini needs a path or standard upload)
    with open("temp_audio.mp3", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.audio(uploaded_file, format='audio/mp3')

    if st.button("Analyze Meeting"):
        with st.spinner("Uploading and processing audio... (This might take a moment)"):
            try:
                # 2. Upload to Gemini
                audio_file = upload_to_gemini("temp_audio.mp3", mime_type="audio/mp3")
                st.success(f"Processed audio duration: {audio_file.name}")

                # 3. Generate Summary & Action Items
                model = genai.GenerativeModel(model_name="gemini-1.5-flash")

                prompt = """
                You are an expert Executive Assistant. Listen to this meeting recording carefully.

                Please provide:
                1. **Executive Summary**: A concise paragraph summarizing the meeting.
                2. **Key Discussion Points**: Bullet points of main topics.
                3. **Action Items**: A checklist of who needs to do what.
                4. **Sentiment Analysis**: What was the general mood of the meeting?
                """

                response = model.generate_content([prompt, audio_file])

                st.markdown("---")
                st.markdown(response.text)

                # Store file in session state for Chatting later
                st.session_state['audio_file'] = audio_file
                st.session_state['chat_active'] = True

            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- CHAT FEATURE (Q&A) ---
if 'chat_active' in st.session_state and st.session_state['chat_active']:
    st.markdown("---")
    st.subheader("💬 Chat with this Meeting")

    user_query = st.text_input("Ask a specific question about the recording (e.g., 'What was the deadline mentioned?')")

    if user_query:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        audio_file = st.session_state['audio_file']

        # We pass the audio file AGAIN with the new question
        response = model.generate_content([user_query, audio_file])
        st.write(response.text)