# NDR Agent — Automated Voice Response System for Failed Deliveries

A smart, voice-based automation system designed to handle **Non-Delivery Reports (NDRs)** by engaging customers through phone calls, interpreting their spoken responses, and updating shipment status accordingly — all without human intervention.

> Built during internship at **eShipz** to reduce manual efforts in last-mile delivery exception handling.

---

## Key Features

- **Automated Calls**: Uses Twilio to contact customers about undelivered packages.
- **Speech to Intent Parsing**: Converts speech to text using Google Speech API, and extracts customer intent (reschedule, cancel, wrong number, etc.).
- **Database Sync**: Updates delivery status and feedback directly in the database.
- **Modular & Extensible**: Easy to integrate with existing NDR or shipment platforms.

---

## Why This Matters

Last-mile delivery failures are a major cost for logistics companies. Manual follow-ups are inefficient and error-prone.  
This agent enables scalable, accurate, and automated voice-based resolution of failed deliveries — improving efficiency, customer experience, and data accuracy.

---

## Tech Stack

| Category          | Tools/Tech Used                                  |
|------------------|--------------------------------------------------|
| Backend          | Python, Flask                                    |
| Voice API        | Twilio Voice API                                 |
| Speech-to-Text   | Google Speech Recognition via `SpeechRecognition` |
| Database         | SQLite3                                          |
| Others           | Ngrok (for local tunneling), dotenv (.env)       |

---

## Project Structure

```

ndr\_agent/
│
├── backend/         # Core Flask logic, APIs, Twilio handlers
│   ├── app.py
│   └── main.py
│
├── schema/          # SQL files to initialize database
│
├── samples/         # Anonymized NDR data samples
│
├── .env.example     # Sample environment configuration
├── README.md
└── requirements.txt

````

---

## Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/ndr_agent.git
   cd ndr_agent
````

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   * Copy `.env.example` to `.env` and fill in your Twilio credentials and ngrok URL.

4. **Initialize the database**

   * Run the SQL scripts in `/schema` using SQLite or a DB browser.

5. **Run the Flask backend**

   ```bash
   python backend/app.py
   ```

6. **Trigger a call**

   ```bash
   python backend/main.py
   ```

---

## Demo Workflow

1. Load failed delivery (NDR) records from DB.
2. Place outbound voice calls via Twilio.
3. Capture customer response and transcribe it.
4. Parse intent (e.g., reschedule/cancel).
5. Update shipment status in the database.

---

## Future Enhancements

* Integrate with NLP models for more advanced intent recognition
* Admin dashboard for live monitoring
* Analytics on NDR reasons and response patterns
* Migrate from SQLite to PostgreSQL/MySQL for production

---

## Author

**Madhubharathi B**

> Developed as part of internship project at **eShipz**

---

