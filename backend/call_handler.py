# call_handler.py
import os
from twilio.rest import Client
from db import get_connection
from dotenv import load_dotenv

load_dotenv()

# Get your Twilio credentials from environment variables for safety
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")  # Your Twilio number
FLASK_ENDPOINT_URL = os.getenv("FLASK_ENDPOINT_URL")  # E.g., https://yourdomain.com/voice

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def get_ndr_shipments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT order_id, receiver_phone FROM shipments
        WHERE tracking_status = 'NDR'
    """)
    shipments = cursor.fetchall()
    conn.close()
    return shipments

def place_call(customer_number,order_id):
    try:
        call = client.calls.create(
            twiml=None,
            to=customer_number,
            from_=TWILIO_FROM_NUMBER,
            url=f"{FLASK_ENDPOINT_URL}/voice?order_id={order_id}"
        )
        print(f"Call placed to {customer_number}, SID: {call.sid}")
        return call.sid
    except Exception as e:
        print(f"Failed to call {customer_number}: {e}")
        return None