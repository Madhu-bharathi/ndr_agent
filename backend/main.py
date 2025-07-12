from call_handler import get_ndr_shipments, place_call

def main():
    print("Fetching NDR shipments from database...")
    shipments = get_ndr_shipments()

    for order_id, receiver_phone in shipments:
        print(f"\n Order ID: {order_id}, 📱 Calling: {receiver_phone}")
        call_sid = place_call(receiver_phone, order_id)

        if not call_sid:
            print(" Call failed. Skipping this shipment...")
            continue

        print(f"Call SID: {call_sid}")
        print("Call placed successfully. Transcription and parsing will happen after user records their response.")
        print("📡 Waiting for Twilio to POST the recording to the Flask webhook...")

if __name__ == "__main__":
    main()
