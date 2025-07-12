# NDR Agent - Automated Failed Delivery Response System

Automates customer interaction for Non-Delivery Reports (NDR) using voice calls, transcription, and intelligent response parsing.

## 🔧 Tech Stack
- Python, Flask
- Twilio Voice API
- SQLite3
- SpeechRecognition, Google Speech-to-Text
- Ngrok (local tunnel)

## Folder Structure
- `backend/`: Core logic
- `schema/`: SQL definitions for DB tables
- `samples/`: Sample data (anonymized)
- `.env.example`: Config variables

## Setup Instructions
1. Clone the repo
2. Run `pip install -r requirements.txt`
3. Set up `.env` using `.env.example`
4. Create DB using schema SQL files
5. Start Flask: `python backend/app.py`
6. Run call trigger: `python backend/main.py`

## Demo Flow
1. Fetch NDR shipments
2. Call customers using Twilio
3. Get and transcribe voice input
4. Parse intent and update database

## Author
Madhubharathi — Built during internship at **eShipz**
