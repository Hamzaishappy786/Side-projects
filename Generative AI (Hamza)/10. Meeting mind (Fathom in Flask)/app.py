import os
import time
from flask import Flask, render_template, request, redirect, url_for
import google.generativeai as genai
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- CONFIGURATION ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Replace with your actual key
os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_audio_with_gemini(file_path, mime_type):
    """Uploads file to Gemini and gets the analysis."""

    # 1. Upload file to Gemini's File API
    gemini_file = genai.upload_file(file_path, mime_type=mime_type)

    # 2. Wait for processing (usually very fast for audio)
    while gemini_file.state.name == "PROCESSING":
        time.sleep(1)
        gemini_file = genai.get_file(gemini_file.name)

    # 3. Generate Content
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = """
    You are an expert AI Meeting Assistant (like Fathom). 
    Listen to this audio recording and generate the following in HTML format (use <h3>, <ul>, <li>, <p>):

    1. <h3>Executive Summary</h3>: A concise summary of the meeting.
    2. <h3>Key Discussion Points</h3>: Bullet points of main topics.
    3. <h3>Action Items</h3>: A clear checklist of who needs to do what.
    4. <h3>Sentiment</h3>: One sentence on the general mood/tone.
    """

    response = model.generate_content([prompt, gemini_file])
    return response.text


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Determine mime type based on extension
            mime_type = "audio/mp3"  # Default
            if filename.endswith('.wav'):
                mime_type = "audio/wav"
            elif filename.endswith('.m4a'):
                mime_type = "audio/x-m4a"

            # Get Analysis
            try:
                analysis = process_audio_with_gemini(filepath, mime_type)
                # Cleanup: remove file after processing to save space
                os.remove(filepath)
                return render_template('index.html', analysis=analysis)
            except Exception as e:
                return f"An error occurred: {e}"

    return render_template('index.html', analysis=None)


if __name__ == '__main__':
    app.run(debug=True)