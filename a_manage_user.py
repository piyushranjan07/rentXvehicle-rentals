from database import get_connection

 
def display_users(cursor, users):

    if not users:
        print("\nNo users found")
        return

    print("\n--- USERS ---")
    for u in users:
        uid, name, dl_no, email, phone, address = u

        # Confirmed bookings = active (Booked) + completed
        cursor.execute("""
            SELECT COUNT(*) FROM bookings WHERE user_id=%s AND status='Booked'
        """, (uid,))
        active_bookings = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM user_history WHERE user_id=%s AND status='Completed'
        """, (uid,))
        completed_bookings = cursor.fetchone()[0]

        total_confirmed = active_bookings + completed_bookings

        # Total revenue from confirmed bookings
        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) FROM bookings WHERE user_id=%s AND status='Booked'
        """, (uid,))
        active_revenue = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) FROM user_history WHERE user_id=%s AND status='Completed'
        """, (uid,))
        completed_revenue = cursor.fetchone()[0]

        total_revenue = active_revenue + completed_revenue

        # Rejection count from user_history
        cursor.execute("""
            SELECT COUNT(*) FROM user_history WHERE user_id=%s AND status='Rejected'
        """, (uid,))
        rejection_count = cursor.fetchone()[0]

        user_dict = {
            "user_id": uid,
            "name": name,
            "dl_no": dl_no,
            "email": email,
            "phone": phone,
            "address": address,
            "confirmed_bookings": total_confirmed if total_confirmed > 0 else "No booking history",
            "total_revenue": total_revenue if total_confirmed > 0 else "N/A",
            "times_rejected": rejection_count if rejection_count > 0 else "No rejections"
        }

        print(user_dict)


def view_users():

    conn = get_connection()
    cursor = conn.cursor()

    print("\n--- VIEW USERS ---")
    print("1. View All Users")
    print("2. Search by User ID")
    print("3. Search by Name")
    print("4. Search by Email")
    print("5. Search by Phone No")
    print("6. Back")

    choice = input("Enter choice: ")

    if choice == "1":
        cursor.execute("SELECT user_id, name, dl_no, email, phone, address FROM users")
        users = cursor.fetchall()
        display_users(cursor, users)

    elif choice == "2":
        uid = input("Enter User ID: ")
        cursor.execute("SELECT user_id, name, dl_no, email, phone, address FROM users WHERE user_id=%s", (uid,))
        users = cursor.fetchall()
        display_users(cursor, users)

    elif choice == "3":
        name = input("Enter Name (or part of name): ")
        cursor.execute("SELECT user_id, name, dl_no, email, phone, address FROM users WHERE name LIKE %s", (f"%{name}%",))
        users = cursor.fetchall()
        display_users(cursor, users)

    elif choice == "4":
        email = input("Enter Email: ")
        cursor.execute("SELECT user_id, name, dl_no, email, phone, address FROM users WHERE email=%s", (email,))
        users = cursor.fetchall()
        display_users(cursor, users)

    elif choice == "5":
        phone = input("Enter Phone No: ")
        cursor.execute("SELECT user_id, name, dl_no, email, phone, address FROM users WHERE phone=%s", (phone,))
        users = cursor.fetchall()
        display_users(cursor, users)

    elif choice == "6":
        cursor.close()
        conn.close()
        return

    else:
        print("Invalid Choice")

    cursor.close()
    conn.close()


def delete_user():

    uid = input("Enter User ID: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE user_id=%s", (uid,))
    conn.commit()

    print("User Deleted")

    cursor.close()
    conn.close()


def customer_menu():

    while True:
        print("\n--- CUSTOMER MANAGEMENT ---")
        print("1. View Users")
        print("2. Delete User")
        print("3. Back")

        choice = input("Enter choice: ")

        match choice:
            case "1": view_users()
            case "2": delete_user()
            case "3": break
            case _: print("Invalid Choice")