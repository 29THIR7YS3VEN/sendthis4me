CREATE TABLE senders (
    id INTEGER,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL,
    city TEXT NOT NULL,
    email_verified_on TEXT,
    email_verified TEXT,
    autofill_name TEXT,
    autofill_phone TEXT,
    autofill_address TEXT
);

CREATE TABLE dispatcher (
    id INTEGER,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    dispatcher_address TEXT NOT NULL,
    orders_per_week TEXT NOT NULL,
    vehicle TEXT,
    passport_number TEXT,
    passport_photo_path TEXT,
    licence_number TEXT,
    licence_photo_path TEXT,
    photo TEXT,
    email_verified TEXT,
    email_verified_on TEXT,
    acceptance TEXT
);

CREATE TABLE orders (
    id INTEGER,
    sender_id INTEGER,
    dispatcher_id INTEGER,
    sender_name TEXT NOT NULL,
    sender_phone TEXT NOT NULL,
    sender_address TEXT NOT NULL,
    receiver_name TEXT NOT NULL,
    receiver_phone TEXT NOT NULL,
    receiver_address TEXT NOT NULL,
    content TEXT NOT NULL,
    package_category TEXT NOT NULL,
    notes TEXT,
    order_status INTEGER,
    created TEXT,
    payment_method TEXT,
    paid TEXT,
    time2 TEXT,
    time3 TEXT,
    time4 TEXT,
    time5 TEXT,
    time6 TEXT,
    time7 TEXT,
    time8 TEXT
);

CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

