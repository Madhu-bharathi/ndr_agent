CREATE TABLE shipments (
  order_id TEXT PRIMARY KEY,
  aws TEXT,
  receiver_name TEXT,
  receiver_phone TEXT,
  receiver_street1 TEXT,
  receiver_postal_code TEXT,
  tracking_status TEXT,
  tracking_sub_status TEXT,
  tracking_pick_date TEXT,
  tracking_expected_delivery TEXT,
  first_ofd_date TEXT,
  delivery_attempts INTEGER,
  parcel_contents TEXT,
  delivery_time TEXT
);
