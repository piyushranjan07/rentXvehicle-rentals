from database import get_connection

 
def view_current_history(user_id):

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
            print(f"\nNo current bookings found for User ID: {user_id}")
            return

        print(f"\n---- CURRENT BOOKINGS (User ID: {user_id}) ----")
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


def view_past_history(user_id):

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
            print(f"\nNo past booking history found for User ID: {user_id}")
            return

        print(f"\n===== PAST BOOKING HISTORY (User ID: {user_id}) =====")
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


def view_all_current_history():

    conn = get_connection()
    if conn is None:
        print("Database connection failed")
        return

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT b.booking_id, b.user_id, u.name, b.vehicle_id, v.type, v.model,
                   b.start_date, b.end_date, b.total_amount,
                   b.status, b.booking_time, b.confirmation_time
            FROM bookings b
            JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            JOIN users u ON b.user_id = u.user_id
            ORDER BY b.user_id, b.booking_time DESC
        """)
        bookings = cursor.fetchall()

        if not bookings:
            print("\nNo current bookings found.")
            return

        print("\n======== ALL CURRENT BOOKINGS ========")
        for b in bookings:
            print({
                "booking_id": b[0],
                "user_id": b[1],
                "user_name": b[2],
                "vehicle_id": b[3],
                "vehicle_type": b[4],
                "vehicle_model": b[5],
                "start_date": b[6],
                "end_date": b[7],
                "total_amount": b[8],
                "status": b[9],
                "booking_time": b[10],
                "confirmation_time": b[11]
            })

    finally:
        cursor.close()
        conn.close()


def view_all_past_history():

    conn = get_connection()
    if conn is None:
        print("Database connection failed")
        return

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT h.booking_id, h.user_id, u.name, h.vehicle_id, v.type, v.model,
                   v.price_per_day, v.discount, h.total_amount,
                   h.start_date, h.end_date, h.booking_time,
                   h.confirmation_time, h.return_time, h.status, h.rating
            FROM user_history h
            JOIN vehicles v ON h.vehicle_id = v.vehicle_id
            JOIN users u ON h.user_id = u.user_id
            ORDER BY h.user_id, h.confirmation_time DESC
        """)
        history = cursor.fetchall()

        if not history:
            print("\nNo past booking history found.")
            return

        print("\n======== ALL PAST BOOKING HISTORY ========")
        for h in history:
            print({
                "booking_id": h[0],
                "user_id": h[1],
                "user_name": h[2],
                "vehicle_id": h[3],
                "vehicle_type": h[4],
                "vehicle_model": h[5],
                "price_per_day": h[6],
                "discount": h[7],
                "total_amount": h[8],
                "start_date": h[9],
                "end_date": h[10],
                "booking_time": h[11],
                "confirmation_time": h[12],
                "return_time": h[13],
                "status": h[14],
                "rating": h[15] if h[15] is not None else "Not Rated"
            })

    finally:
        cursor.close()
        conn.close()


def validate_user(user_id):
    conn = get_connection()
    if conn is None:
        print("Database connection failed")
        return None

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT user_id, name, dl_no, email, phone, address FROM users WHERE user_id=%s",
            (user_id,)
        )
        user = cursor.fetchone()
        if user:
            return user
        else:
            print(f"\nNo user found with User ID: {user_id}")
            return None
    finally:
        cursor.close()
        conn.close()


def user_history_menu():

    user_id = input("\nEnter User ID: ")

    if user_id.lower() == "all":
        while True:
            print("\n---- ALL USERS BOOKING HISTORY ----")
            print("1. Current Bookings")
            print("2. Past Bookings")
            print("3. Back")

            choice = input("Enter choice: ")

            match choice:
                case "1":
                    view_all_current_history()
                case "2":
                    view_all_past_history()
                case "3":
                    break
                case _:
                    print("Invalid Choice")
        return

    user = validate_user(user_id)
    if not user:
        return

    print("\n----- USER INFORMATION -----")
    print(f"  User ID  : {user[0]}")
    print(f"  Name     : {user[1]}")
    print(f"  DL No.   : {user[2]}")
    print(f"  Email    : {user[3]}")
    print(f"  Phone    : {user[4]}")
    print(f"  Address  : {user[5]}")
    print("----------------------------")

    while True:
        print(f"\n---- USER BOOKING HISTORY (User ID: {user_id}) ----")
        print("1. Current Bookings")
        print("2. Past Bookings")
        print("3. Back")

        choice = input("Enter choice: ")

        match choice:
            case "1":
                view_current_history(user_id)
            case "2":
                view_past_history(user_id)
            case "3":
                break
            case _:
                print("Invalid Choice")
