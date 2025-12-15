import os
import time
import speech_recognition as sr
from gtts import gTTS
import pygame
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load Environment Variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 2. Setup Gemini (The Brain)
# We set a system prompt to make it act like a helpful assistant
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=GOOGLE_API_KEY,
    convert_system_message_to_human=True
)

# Initialize Pygame Mixer for playing audio
pygame.mixer.init()


def speak(text):
    """
    Converts text to speech and plays it immediately.
    """
    try:
        # Generate audio file
        tts = gTTS(text=text, lang='en', slow=False)
        filename = "temp_voice.mp3"

        # Save and play
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        # Wait until audio is finished playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Cleanup
        pygame.mixer.music.unload()
        os.remove(filename)
    except Exception as e:
        print(f"Error in speech playback: {e}")


def listen():
    """
    Listens to the microphone and returns text.
    """
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\n🎤 Listening... (Speak now)")

        # Adjust for ambient noise (helps if you have a fan running)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            # Listen with a timeout so it doesn't hang forever
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("⏳ Processing audio...")

            # Convert audio to text using Google's free recognizer
            text = recognizer.recognize_google(audio)
            print(f"🗣️  You said: {text}")
            return text

        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError:
            print("Could not request results (check internet).")
            return None


def main():
    print("🤖 AI Voice Assistant Initialized")
    print("---------------------------------")
    speak("System online. How can I help you today?")

    conversation_history = [
        {"role": "system",
         "content": "You are a helpful, concise AI voice assistant. Keep your answers short (1-2 sentences) and conversational."}
    ]

    while True:
        user_input = listen()

        if user_input:
            # Exit command
            if "exit" in user_input.lower() or "stop" in user_input.lower():
                speak("Shutting down. Goodbye!")
                break

            # Add user query to context (simple context handling)
            # For a full chat history, you'd use LangChain memory, but this keeps it simple
            prompt = f"User said: {user_input}. Reply conversationally."

            try:
                # Get response from Gemini
                response = llm.invoke(prompt)
                ai_text = response.content

                print(f"🤖 AI: {ai_text}")
                speak(ai_text)

            except Exception as e:
                print(f"Error communicating with Gemini: {e}")
                speak("I'm having trouble thinking right now.")


if __name__ == "__main__":
    main()