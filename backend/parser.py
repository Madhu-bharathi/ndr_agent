import sqlite3
import re
import dateparser
from datetime import datetime, timedelta
from difflib import get_close_matches
from dateparser.search import search_dates


DB_PATH = "responses.db"

def extract_new_address(text):
    text_lower = text.lower()
    address_phrases = [
        "change my address to",
        "my new address is",
        "update address to",
        "address is",
        "new address is",
    ]
    for phrase in address_phrases:
        if phrase in text_lower:
            start_index = text_lower.find(phrase) + len(phrase)
            new_address = text[start_index:].strip(" .:")
            return text[start_index:].strip(" .:") if new_address else "No new address detected"
    return None



def extract_mobile_number(text):
    digits_only = re.sub(r"\D", "", text)
    if digits_only.endswith("91") and len(digits_only) == 12:
        return digits_only[-10:]  # Just return last 10 digits
    elif len(digits_only) == 10:
        return digits_only
    return "Invalid or missing number"

import re
from datetime import datetime, timedelta
from dateparser.search import search_dates

import re
from datetime import datetime, timedelta
from dateparser.search import search_dates

def extract_datetime(text):
    text = text.lower()
    now = datetime.now()
    date_obj = None
    time_obj = None

    print("\n--- DEBUG ---")
    print("Original text:", text)

    # Match time like "5:00 p.m.", "5pm", "5:30 a.m.", etc.
    time_match = re.search(r"(?:at\s*)?(\d{1,2})(:\d{2})?\s*(a\.?m\.?|p\.?m\.?)", text)
    print("Time match:", time_match.group(0) if time_match else "None")

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)[1:]) if time_match.group(2) else 0
        am_pm = time_match.group(3).replace(".", "")  # Normalize: "p.m." → "pm"

        if am_pm == "pm" and hour != 12:
            hour += 12
        elif am_pm == "am" and hour == 12:
            hour = 0

        time_obj = (hour, minute)

    # Keyword checks
    if "today" in text:
        date_obj = now
    elif "tomorrow" in text:
        date_obj = now + timedelta(days=1)

    # Dateparser
    if not date_obj:
        parsed = search_dates(
            text,
            settings={
                'DATE_ORDER': 'DMY',
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': now,
            }
        )
        print("Parsed dates:", parsed)
        if parsed:
            for _, dt in parsed:
                if dt >= now:
                    date_obj = dt
                    break

    # Combine date + time
    if date_obj:
        if time_obj:
            date_obj = date_obj.replace(hour=time_obj[0], minute=time_obj[1])
            return date_obj.strftime("%d-%m-%Y at %I:%M %p")
        return date_obj.strftime("%d-%m-%Y (Time not mentioned)")
    elif time_obj:
        temp_time = now.replace(hour=time_obj[0], minute=time_obj[1])
        return temp_time.strftime("%I:%M %p (Date not mentioned)")

    return "Invalid or vague date/time. Please provide exact date and time."


def detect_action_and_value(text):
    text_lower = text.lower()

    def fuzzy_contains(word, choices):
        matches = get_close_matches(word, choices, n=1, cutoff=0.8)
        return bool(matches)

    # Reschedule / Re-attempt
    if (
    fuzzy_contains("reschedule", text_lower.split())
    or "re-attempt" in text_lower
    or "redeliver" in text_lower
    or "schedule" in text_lower
    ):
        datetime_value = extract_datetime(text)
        if "could not parse" in datetime_value.lower():
           return "Re-attempt", "Invalid or vague date/time. Please provide exact date and time."
        return "Re-attempt", datetime_value

    elif any(phrase in text_lower for phrase in [
      "delivery cancel",
      "return the package", 
      "return parcel", 
      "send it back", 
      "cancel order", 
      "return",
      "rto", 
      "return to origin", 
      "send back",
      "return the package to origin"
    ]):
        return "RTO", "Return to Origin requested"

    elif any(phrase in text_lower for phrase in [
      "change my address to", 
      "my new address is", 
      "update address to", 
      "address is", 
      "new address is",
      "change address", 
      "new address", 
      "update address", 
      "landmark"
    ]):

       new_address = extract_new_address(text)
       if new_address:
          return "Change Landmark", new_address
       else:
          return "Change Landmark", "No new address detected"


    elif any(phrase in text_lower for phrase in [
      "change my number to", 
      "my new number is", 
      "update number to", 
      "number is", 
      "new number is",
      "change number", 
      "new number", 
      "update number", 
      "number",
      "alternate number"
     ]):
         number = extract_mobile_number(text)
         return "Alternate mobile number", number

    return "Unknown", "Could not understand intent"

def process_latest_response():
    RESPONSES_DB = "responses.db"
    SHIPMENTS_DB = "ndr_agent.db"

    # First DB connection: responses.db
    conn1 = sqlite3.connect(RESPONSES_DB)
    cursor1 = conn1.cursor()

    cursor1.execute('''
        SELECT id, shipment_id, response_text FROM customer_responses
        WHERE response_text IS NOT NULL AND parsed_action IS NULL
        ORDER BY call_time DESC LIMIT 1
    ''')
    row = cursor1.fetchone()

    if not row:
        print("No new responses to process.")
        return

    response_id, shipment_id, response_text = row
    action, value = detect_action_and_value(response_text)

    # Update response as processed
    cursor1.execute('''
        UPDATE customer_responses
        SET parsed_action = ?, parsed_value = ?, processed = 1
        WHERE id = ?
    ''', (action, value, response_id))
    conn1.commit()
    conn1.close()  # ✅ Done with responses.db

    print(f"Parsed response ID {response_id}:")
    print(f"   Action: {action}")
    print(f"   Value: {value}")

    # Second DB connection: ndr_agent.db
    conn2 = sqlite3.connect(SHIPMENTS_DB)
    cursor2 = conn2.cursor()

    if action == "Re-attempt":
        if " at " in value:
            date_part, time_part = value.split(" at ")
            cursor2.execute('''
                UPDATE shipments
                SET tracking_expected_delivery = ?, delivery_time = ?
                WHERE order_id = ?
            ''', (date_part.strip(), time_part.strip(), shipment_id))
        elif "Time not mentioned" in value:
            date_part = value.split(" ")[0]
            cursor2.execute('''
                UPDATE shipments
                SET tracking_expected_delivery = ?
                WHERE order_id = ?
            ''', (date_part.strip(), shipment_id))
        elif "Date not mentioned" in value:
            time_part = value.split(" ")[0]
            cursor2.execute('''
                UPDATE shipments
                SET delivery_time = ?
                WHERE order_id = ?
            ''', (time_part.strip(), shipment_id))

    elif action == "Change Landmark":
        cursor2.execute('''
            UPDATE shipments
            SET receiver_street1 = ?
            WHERE order_id = ?
        ''', (value, shipment_id))

    elif action == "Alternate mobile number":
        cursor2.execute('''
            UPDATE shipments
            SET receiver_phone = ?
            WHERE order_id = ?
        ''', (value, shipment_id))

    elif action == "RTO":
        cursor2.execute('''
            UPDATE shipments
            SET tracking_status = 'RTO'
            WHERE order_id = ?
        ''', (shipment_id,))

    conn2.commit()
    conn2.close()  # Done with ndr_agent.db


