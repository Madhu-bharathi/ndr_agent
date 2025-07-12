import requests
from requests.auth import HTTPBasicAuth
import speech_recognition as sr
from pydub import AudioSegment, effects
import os
import uuid
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Database path
DB_PATH = "responses.db"

def download_and_transcribe_and_update(call_sid, recording_url):
    if not recording_url.endswith(".mp3"):
        recording_url += ".mp3"

    # Generate unique filenames
    uid = str(uuid.uuid4())
    mp3_filename = f"{uid}.mp3"
    wav_filename = f"{uid}.wav"

    # Step 1: Download the MP3
    response = requests.get(recording_url, auth=HTTPBasicAuth(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")))
    with open(mp3_filename, "wb") as f:
        f.write(response.content)

    # Step 2: Convert to WAV for transcription (with normalization)
    # Step 2: Convert to WAV for transcription (with normalization + silence at end)
    audio = AudioSegment.from_mp3(mp3_filename)
    audio = effects.normalize(audio)
    audio += AudioSegment.silent(duration=2000)  # Add 2 seconds of silence at end
    audio.export(wav_filename, format="wav")


    # Step 3: Transcribe the audio
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_filename) as source:
        audio_data = recognizer.record(source)  # Capture full audio without loss

        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "Could not understand audio"
        except sr.RequestError as e:
            text = f"Speech Recognition error: {e}"

    # Step 4: Cleanup
    os.remove(mp3_filename)
    os.remove(wav_filename)

    # Step 5: Update database with transcribed text
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE customer_responses
        SET response_text = ?
        WHERE call_sid = ?
    ''', (text, call_sid))
    conn.commit()
    conn.close()

    return text
