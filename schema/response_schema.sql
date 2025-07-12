CREATE TABLE customer_responses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  call_sid TEXT,
  shipment_id TEXT,
  customer_number TEXT,
  audio_url TEXT,
  response_text TEXT,
  parsed_action TEXT,
  parsed_value TEXT,
  call_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed BOOLEAN DEFAULT 0
);
