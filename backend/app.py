from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import sqlite3
import os

from transcriber import download_and_transcribe_and_update
from parser import process_latest_response

app = Flask(__name__)
DB_PATH = "responses.db"

@app.route("/voice", methods=["POST", "HEAD"])
def voice():
    if request.method == "HEAD":
        return "", 200  # Twilio's webhook verification

    shipment_id = request.args.get("order_id", "unknown")
    print(f"\n Incoming call request from Twilio for shipment ID: {shipment_id}")

    response = VoiceResponse()
    response.say(
        "Hello! This is an automated call from Eshipz regarding your recent delivery attempt. "
        "Please explain what you'd like to do after the beep. ",
        # "You may say: reschedule delivery, return to origin, update address, or provide a new phone number."
        voice="alice"
    )
    response.record(
        timeout=9,
        maxLength=140,
        action=f"/handle_recording?shipment_id={shipment_id}",
        method="POST"
    )
    
    return str(response)

@app.route("/handle_recording", methods=["POST"])
def handle_recording():
    call_sid = request.form.get("CallSid")
    recording_url = request.form.get("RecordingUrl")
    from_number = request.form.get("From")
    to_number = request.form.get("To")
    twilio_number = os.getenv("TWILIO_NUMBER", "+1234567890")
    customer_number = to_number if from_number == twilio_number else from_number
    shipment_id = request.args.get("shipment_id", "unknown")

    if not call_sid or not recording_url:
        print("Missing CallSid or RecordingUrl. Cannot proceed.")
        return "Missing required data", 400

    print(f"\n Received recording for Call SID: {call_sid}")
    print(f"Recording URL: {recording_url}.mp3")
    print(f"Shipment ID: {shipment_id}, 📱 Customer Number: {customer_number}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customer_responses (
                call_sid,
                shipment_id,
                customer_number,
                audio_url,
                response_text,
                parsed_action,
                parsed_value,
                processed
            ) VALUES (?, ?, ?, ?, NULL, NULL, NULL, 0)
        ''', (call_sid, shipment_id, customer_number, recording_url + ".mp3"))
        conn.commit()
        conn.close()
        print("Recording details saved to database.")

        # Transcribe the voice message
        print(f" Starting transcription for Call SID: {call_sid}...")
        transcribed_text = download_and_transcribe_and_update(call_sid, recording_url + ".mp3")
        print(f"Transcription result: {transcribed_text}")

        # Parse the response
        print("Parsing the response and updating database...")
        process_latest_response()
        print("Response parsed and database updated.")

        # Respond to Twilio
        response = VoiceResponse()
        response.say("Thank you. We have received your response.", voice="alice")
        response.hangup()
        return str(response), 200

    except Exception as e:
        print("Error during recording handling, transcription, or parsing:", e)
        return "Internal server error", 500


if __name__ == "__main__":
    print("Flask server running. Ready to handle incoming voice calls.")
    app.run(port=5000, debug=True)
