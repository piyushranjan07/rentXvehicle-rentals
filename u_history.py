from database import get_connection
 

def current_history(user_id):

    conn = get_connection()
    if conn is None:
        print("Database connection failed")
        return

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT b.booking_id, b.vehicle_id, v.type, v.model,
                   b.start_date, b.end_date, b.total_amount,
                   b.status, b.booking_time, b.confirmation_time
            FROM bookings b
            JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            WHERE b.user_id=%s
            ORDER BY b.booking_time DESC
        """, (user_id,))
        bookings = cursor.fetchall()

        if not bookings:
            print("\nNo current bookings found.")
            return

        print("\n===== CURRENT BOOKINGS =====")
        for b in bookings:
            print({
                "booking_id": b[0],
                "vehicle_id": b[1],
                "vehicle_type": b[2],
                "vehicle_model": b[3],
                "start_date": b[4],
                "end_date": b[5],
                "total_amount": b[6],
                "status": b[7],
                "booking_time": b[8],
                "confirmation_time": b[9]
            })

    finally:
        cursor.close()
        conn.close()


def past_history(user_id):

    conn = get_connection()
    if conn is None:
        print("Database connection failed")
        return

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT h.booking_id, h.vehicle_id, v.type, v.model,
                   v.price_per_day, v.discount, h.total_amount,
                   h.start_date, h.end_date, h.booking_time,
                   h.confirmation_time, h.return_time, h.status, h.rating
            FROM user_history h
            JOIN vehicles v ON h.vehicle_id = v.vehicle_id
            WHERE h.user_id=%s
            ORDER BY h.confirmation_time DESC
        """, (user_id,))
        history = cursor.fetchall()

        if not history:
            print("\nNo past booking history found.")
            return

        print("\n===== PAST BOOKING HISTORY =====")
        for h in history:
            print({
                "booking_id": h[0],
                "vehicle_id": h[1],
                "vehicle_type": h[2],
                "vehicle_model": h[3],
                "price_per_day": h[4],
                "discount": h[5],
                "total_amount": h[6],
                "start_date": h[7],
                "end_date": h[8],
                "booking_time": h[9],
                "confirmation_time": h[10],
                "return_time": h[11],
                "status": h[12],
                "rating": h[13] if h[13] is not None else "Not Rated"
            })

    finally:
        cursor.close()
        conn.close()

    # Ask user if they want to rate
    rate_choice = input("\nDo you want to rate your bookings? (Y/N): ").strip().upper()
    if rate_choice == "Y":
        rate_booking(user_id)


def rate_booking(user_id):

    conn = get_connection()
    if conn is None:
        print("Database connection failed")
        return

    cursor = conn.cursor()

    try:
        # Fetch only completed & unrated bookings
        cursor.execute("""
            SELECT h.booking_id, h.vehicle_id, v.type, v.model,
                   h.start_date, h.end_date, h.total_amount
            FROM user_history h
            JOIN vehicles v ON h.vehicle_id = v.vehicle_id
            WHERE h.user_id=%s AND h.status='Completed' AND h.rating IS NULL
            ORDER BY h.return_time DESC
        """, (user_id,))
        unrated = cursor.fetchall()

        if not unrated:
            print("\nNo bookings available to rate.")
            return

        print("\n--- BOOKINGS AVAILABLE TO RATE ---")
        for b in unrated:
            print({
                "booking_id": b[0],
                "vehicle_id": b[1],
                "vehicle_type": b[2],
                "vehicle_model": b[3],
                "start_date": b[4],
                "end_date": b[5],
                "total_amount": b[6]
            })

        booking_id = input("\nEnter Booking ID to rate: ")

        # Verify the booking belongs to user, is completed, and unrated
        cursor.execute("""
            SELECT booking_id FROM user_history
            WHERE booking_id=%s AND user_id=%s AND status='Completed' AND rating IS NULL
        """, (booking_id, user_id))
        record = cursor.fetchone()

        if record is None:
            print("Invalid Booking ID or already rated.")
            return

        rating_input = input("Enter rating (1-5): ").strip()

        try:
            rating = float(rating_input)
        except ValueError:
            print("Invalid input. Rating must be a number.")
            return

        if rating < 1 or rating > 5:
            print("Rating must be between 1 and 5.")
            return

        cursor.execute("""
            UPDATE user_history SET rating=%s
            WHERE booking_id=%s AND user_id=%s AND status='Completed'
        """, (rating, booking_id, user_id))

        conn.commit()
        print(f"Thanks for Rating!!, Hope you enjoyed our service...")

    finally:
        cursor.close()
        conn.close()


def booking_history(user_id):

    while True:
        print("\n--- BOOKING HISTORY ---")
        print("1. Current Bookings")
        print("2. Past Bookings")
        print("3. Back")

        choice = input("Enter choice: ")

        match choice:
            case "1":
                current_history(user_id)
            case "2":
                past_history(user_id)
            case "3":
                break
            case _:
                print("Invalid Choice")
