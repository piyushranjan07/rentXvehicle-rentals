import uuid
from datetime import datetime
from database import get_connection
from mail_service import send_booking_init_mail

 
def create_booking(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch user email
    cursor.execute("SELECT email FROM users WHERE user_id=%s", (user_id,))
    user_data = cursor.fetchone()

    if user_data is None:
        print("User not found")
        return

    email = user_data[0]

    # Show available vehicles
    cursor.execute("""
        SELECT vehicle_id, model, price_per_day, discount
        FROM vehicles
        WHERE status='Available'
    """)
    vehicles = cursor.fetchall()

    if not vehicles:
        print("No vehicles available")
        return

    print("\n--- AVAILABLE VEHICLES ---")
    for v in vehicles:
        print(v)

    # Take input
    vehicle_id = input("Enter Vehicle ID: ")
    start_date = input("Enter Start Date (YYYY-MM-DD): ")
    end_date = input("Enter End Date (YYYY-MM-DD): ")

    # Fetch price
    cursor.execute("""
        SELECT type, model, price_per_day, discount FROM vehicles WHERE vehicle_id=%s
    """, (vehicle_id,))
    data = cursor.fetchone()

    if data is None:
        print("Invalid Vehicle ID")
        return

    vtype, model, price, discount = data

    if discount is None:
        discount = 0

    final_price = price - (price * discount / 100)

    # Calculate days
    d1 = datetime.strptime(start_date, "%Y-%m-%d")
    d2 = datetime.strptime(end_date, "%Y-%m-%d")

    days = (d2 - d1).days + 1

    if days <= 0:
        print("Invalid date range")
        return

    total_amount = days * final_price

    booking_id = str(uuid.uuid4()).replace("-", "")[:5]
    booking_time = datetime.now()

    # Insert booking
    cursor.execute("""
        INSERT INTO bookings 
        (booking_id, user_id, vehicle_id, start_date, end_date, total_amount, status, booking_time)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (booking_id, user_id, vehicle_id, start_date, end_date, total_amount, "Pending", booking_time))

    conn.commit()

    # Send mail
    send_booking_init_mail(email, booking_id, vehicle_id, vtype, model, start_date, end_date, total_amount)

    print("Booking Created Successfully")
    print("Visit office for payment & confirmation")

    cursor.close()
    conn.close()