import streamlit as st
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# --- CONFIGURATION ---
# Replace with your actual API key or use os.getenv("GOOGLE_API_KEY") if you use .env
os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


# --- HELPER FUNCTIONS ---

def extract_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    Examples:
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ -> dQw4w9WgXcQ
    - https://youtu.be/dQw4w9WgXcQ -> dQw4w9WgXcQ
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = parse_qs(parsed_url.query)
            return p['v'][0]
    return None


def get_transcript_text(video_id):
    """
    Fetches the transcript and combines it into a single string.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # The transcript is a list of dictionaries. We just want the 'text'.
        text = " ".join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        return f"Error fetching transcript: {e}"


def generate_summary(transcript_text):
    """
    Sends the transcript to Gemini for summarization.
    """
    prompt = f"""
    You are a professional video summarizer. 
    Please read the following YouTube video transcript and provide a summary.

    Structure your response as follows:
    1. **Title**: A catchy title for the summary.
    2. **The Gist**: A 2-3 sentence high-level overview.
    3. **Key Takeaways**: Bullet points of the most important insights.

    Transcript:
    {transcript_text}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")  # Flash is faster/cheaper for this
    response = model.generate_content(prompt)
    return response.text


# --- STREAMLIT UI ---

st.title("📺 TubeMind: YouTube Summarizer")
st.markdown("Paste a YouTube link below to get a quick summary using **Gemini AI**.")

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)

    if video_id:
        # Display the video thumbnail so user knows it worked
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

        if st.button("Get Summary"):
            with st.spinner("Transcribing and Thinking..."):
                # 1. Get Transcript
                transcript_text = get_transcript_text(video_id)

                if "Error" in transcript_text:
                    st.error(transcript_text)
                else:
                    # 2. Get Summary from Gemini
                    summary = generate_summary(transcript_text)

                    # 3. Display Result
                    st.markdown("## 📝 Summary")
                    st.markdown(summary)
    else:
        st.error("Invalid YouTube URL. Please use a standard URL.")