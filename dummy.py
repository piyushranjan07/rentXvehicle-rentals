import random
import string
from datetime import datetime, timedelta
from database import get_connection

# DB connection
conn = get_connection()
cursor = conn.cursor()

# Fetch users and vehicles
cursor.execute("SELECT user_id FROM users")
users = [u[0] for u in cursor.fetchall()]

cursor.execute("SELECT vehicle_id, price_per_day FROM vehicles")
vehicles = cursor.fetchall()

# Generate random 5-char booking id
def generate_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

# Date range
start_range = datetime(2026,2 , 1)
end_range = datetime(2026, 2, 28)

records = []

for _ in range(60):  # generate 120 records

    booking_id = generate_id()
    user_id = random.choice(users)
    vehicle_id, price = random.choice(vehicles)

    # Random start date
    start_date = start_range + timedelta(days=random.randint(0, 40))

    # Random duration (1–5 days)
    duration = random.randint(1, 5)
    end_date = start_date + timedelta(days=duration)

    # Booking timestamps
    booking_time = start_date + timedelta(
        hours=random.randint(8, 20),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

    confirmation_time = booking_time + timedelta(minutes=random.randint(1, 10))

    # 80% completed bookings
    if random.random() < 0.8:
        status = "Completed"

        return_time = end_date - timedelta(days=random.randint(0, 1)) + timedelta(
            hours=random.randint(8, 20),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )

        rating = round(random.uniform(3.0, 5.0), 1)

    else:
        status = "Booked"
        return_time = None
        rating = None

    # Full booking charge (your rule)
    days = (end_date - start_date).days + 1
    total_amount = days * price

    records.append((
        booking_id, user_id, vehicle_id,
        start_date.date(), end_date.date(),
        booking_time, confirmation_time, return_time,
        total_amount, status, rating
    ))

# Insert query
query = """
INSERT INTO user_history (
    booking_id, user_id, vehicle_id,
    start_date, end_date,
    booking_time, confirmation_time, return_time,
    total_amount, status, rating
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

cursor.executemany(query, records)
conn.commit()

print("✅ Dummy data inserted successfully!")

cursor.close()
conn.close()