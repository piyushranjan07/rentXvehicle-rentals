from datetime import datetime
from database import get_connection
from mail_service import send_return_mail
 
def return_vehicle():

    conn = get_connection()
    cursor = conn.cursor()

    # Show active bookings
    cursor.execute("""
        SELECT b.booking_id, b.user_id, u.name, u.address,
               b.vehicle_id, v.type, v.model, b.total_amount
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        WHERE b.status='Booked'
    """)
    bookings = cursor.fetchall()

    if not bookings:
        print("No active bookings")
        return

    print("\n--- ACTIVE BOOKINGS ---")
    booking_list = []
    for b in bookings:
        booking_dict = {
            "booking_id": b[0],
            "user_id": b[1],
            "user_name": b[2],
            "address": b[3],
            "vehicle_id": b[4],
            "vehicle_type": b[5],
            "vehicle_model": b[6],
            "total_amount": b[7]
        }
        booking_list.append(booking_dict)

    for booking in booking_list:
        print(booking)

    booking_id = input("Enter Booking ID to RETURN: ")

    # Fetch full booking details
    cursor.execute("""
        SELECT user_id, vehicle_id, start_date, end_date, total_amount, confirmation_time, booking_time
        FROM bookings WHERE booking_id=%s
    """, (booking_id,))
    data = cursor.fetchone()

    if data is None:
        print("Invalid Booking ID")
        return

    user_id, vehicle_id, start_date, end_date, total_amount, confirmation_time, booking_time = data

    # Get user details
    cursor.execute("SELECT name, email FROM users WHERE user_id=%s", (user_id,))
    user_name, email = cursor.fetchone()

    # Get vehicle details
    cursor.execute("""
        SELECT type, model
        FROM vehicles WHERE vehicle_id=%s
    """, (vehicle_id,))
    vtype, model = cursor.fetchone()

    return_time = datetime.now()

    # COPY BOOKING INTO USER HISTORY
    cursor.execute("""
        INSERT INTO user_history
        (booking_id, user_id, vehicle_id,
         start_date, end_date,
         booking_time, confirmation_time, return_time, total_amount, status)
        SELECT booking_id, user_id, vehicle_id,
               start_date, end_date,
               booking_time, confirmation_time, %s, total_amount, 'Completed'
        FROM bookings WHERE booking_id=%s
    """, (return_time, booking_id))

    # UPDATE VEHICLE STATUS → Available
    cursor.execute("""
        UPDATE vehicles SET status='Available' WHERE vehicle_id=%s
    """, (vehicle_id,))

    # DELETE FROM BOOKINGS
    cursor.execute("""
        DELETE FROM bookings WHERE booking_id=%s
    """, (booking_id,))

    conn.commit()

    # SEND EMAIL
    send_return_mail(email, booking_id, vehicle_id, vtype, model, total_amount)

    print("Vehicle Returned, History Stored & Booking Removed")

    cursor.close()
    conn.close()