from datetime import datetime
from database import get_connection 
from mail_service import send_booking_confirm_mail, send_booking_reject_mail, send_vehicle_change_mail


def accept_booking():

    conn = get_connection()
    cursor = conn.cursor()

    # Show pending bookings
    cursor.execute("""
        SELECT b.booking_id, b.user_id, u.name, u.address,
               b.vehicle_id, v.type, v.model, b.start_date, b.end_date, b.total_amount
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN vehicles v ON b.vehicle_id = v.vehicle_id
        WHERE b.status='Pending'
    """)
    bookings = cursor.fetchall()

    if not bookings:
        print("No bookings available")
        cursor.close()
        conn.close()
        return

    print("\n--- PENDING BOOKINGS ---")
    for b in bookings:
        print({
            "booking_id": b[0],
            "user_id": b[1],
            "user_name": b[2],
            "address": b[3],
            "vehicle_id": b[4],
            "vehicle_type": b[5],
            "vehicle_model": b[6],
            "start_date": b[7],
            "end_date": b[8],
            "total_amount": b[9]
        })

    booking_id = input("Enter Booking ID to ACCEPT: ")

    # Get booking details
    cursor.execute("""
        SELECT user_id, vehicle_id, start_date, end_date, total_amount, booking_time
        FROM bookings WHERE booking_id=%s AND status='Pending'
    """, (booking_id,))
    data = cursor.fetchone()

    if data is None:
        print("Invalid Booking ID")
        cursor.close()
        conn.close()
        return

    user_id, vehicle_id, start_date, end_date, total_amount, booking_time = data

    # Get user info
    cursor.execute("SELECT name, email FROM users WHERE user_id=%s", (user_id,))
    user_name, email = cursor.fetchone()

    # Get vehicle info
    cursor.execute("""
        SELECT type, model FROM vehicles WHERE vehicle_id=%s
    """, (vehicle_id,))
    vtype, model = cursor.fetchone()

    # CHECK DATE CONFLICT with already Booked bookings
    cursor.execute("""
        SELECT booking_id FROM bookings
        WHERE vehicle_id=%s AND status='Booked'
        AND NOT (%s > end_date OR %s < start_date)
    """, (vehicle_id, start_date, end_date))

    conflict = cursor.fetchone()

    if not conflict:
        final_vehicle_id = vehicle_id

    else:
        print("Conflict detected with an existing booking, searching another vehicle...")

        # FIND ALTERNATIVE VEHICLE (same type & model)
        cursor.execute("""
            SELECT vehicle_id FROM vehicles
            WHERE type=%s AND model=%s AND vehicle_id != %s
        """, (vtype, model, vehicle_id))

        vehicles = cursor.fetchall()

        final_vehicle_id = None

        for v in vehicles:
            vid = v[0]

            # check conflict for this vehicle
            cursor.execute("""
                SELECT booking_id FROM bookings
                WHERE vehicle_id=%s AND status='Booked'
                AND NOT (%s > end_date OR %s < start_date)
            """, (vid, start_date, end_date))

            if not cursor.fetchone():
                final_vehicle_id = vid
                break

        # NO VEHICLE FOUND -> REJECT
        if final_vehicle_id is None:

            print("No alternative vehicle available. Rejecting booking...")

            rejection_time = datetime.now()

            # Copy booking into history
            cursor.execute("""
                INSERT INTO user_history
                (booking_id, user_id, vehicle_id,
                 start_date, end_date,
                 booking_time, confirmation_time, return_time, total_amount, status)
                SELECT booking_id, user_id, vehicle_id,
                       start_date, end_date,
                       booking_time, %s, NULL, total_amount, 'Rejected'
                FROM bookings WHERE booking_id=%s
            """, (rejection_time, booking_id))

            # delete booking
            cursor.execute("DELETE FROM bookings WHERE booking_id=%s", (booking_id,))

            conn.commit()

            send_booking_reject_mail(
                email, booking_id, vehicle_id,
                vtype, model, start_date, end_date, total_amount
            )

            cursor.close()
            conn.close()
            return

    # CONFIRM BOOKING
    confirmation_time = datetime.now()

    cursor.execute("""
        UPDATE bookings
        SET status='Booked',
            confirmation_time=%s,
            vehicle_id=%s
        WHERE booking_id=%s
    """, (confirmation_time, final_vehicle_id, booking_id))

    # update vehicle status
    cursor.execute("""
        UPDATE vehicles SET status='Rented' WHERE vehicle_id=%s
    """, (final_vehicle_id,))

    conn.commit()

    # Send appropriate mail
    if final_vehicle_id != vehicle_id:
        send_vehicle_change_mail(
            email,
            booking_id,
            vehicle_id,          
            final_vehicle_id,    
            vtype,
            model,
            start_date,
            end_date,
            total_amount
        )
        print("Booking confirmed with vehicle change. Mail sent.")
    else:
        send_booking_confirm_mail(
            email, booking_id, final_vehicle_id,
            vtype, model, start_date, end_date, total_amount
        )
        print("Booking confirmed (no vehicle change)")

    # CHECK OTHER PENDING BOOKINGS

    cursor.execute("""
        SELECT booking_id, user_id, start_date, end_date, total_amount, booking_time
        FROM bookings
        WHERE vehicle_id=%s AND status='Pending' AND booking_id != %s
    """, (vehicle_id, booking_id))

    pending_bookings = cursor.fetchall()

    for pb in pending_bookings:
        pb_booking_id, pb_user_id, pb_start, pb_end, pb_total, pb_booking_time = pb

        if not (pb_start > end_date or pb_end < start_date):

            print(f"\n Conflict found: Booking {pb_booking_id} overlaps with confirmed booking {booking_id}")

            cursor.execute("SELECT name, email FROM users WHERE user_id=%s", (pb_user_id,))
            pb_user_name, pb_email = cursor.fetchone()

            cursor.execute("""
                SELECT vehicle_id FROM vehicles
                WHERE type=%s AND model=%s AND vehicle_id != %s
            """, (vtype, model, vehicle_id))

            alt_vehicles = cursor.fetchall()
            new_vehicle_id = None

            for av in alt_vehicles:
                avid = av[0]

                cursor.execute("""
                    SELECT booking_id FROM bookings
                    WHERE vehicle_id=%s AND status='Booked'
                    AND NOT (%s > end_date OR %s < start_date)
                """, (avid, pb_start, pb_end))

                if not cursor.fetchone():
                    cursor.execute("""
                        SELECT booking_id FROM bookings
                        WHERE vehicle_id=%s AND status='Pending'
                        AND NOT (%s > end_date OR %s < start_date)
                        AND booking_id != %s
                    """, (avid, pb_start, pb_end, pb_booking_id))

                    if not cursor.fetchone():
                        new_vehicle_id = avid
                        break

            if new_vehicle_id:
                cursor.execute("""
                    UPDATE bookings SET vehicle_id=%s WHERE booking_id=%s
                """, (new_vehicle_id, pb_booking_id))

                conn.commit()

                send_vehicle_change_mail(
                    pb_email,
                    pb_booking_id,
                    vehicle_id,        # old vehicle
                    new_vehicle_id,    # new vehicle
                    vtype,
                    model,
                    pb_start,
                    pb_end,
                    pb_total
                )

                print(f"Booking {pb_booking_id}: Reassigned to vehicle {new_vehicle_id}. Mail sent to {pb_email}")

            else:
                print(f"Booking {pb_booking_id}: No alternative vehicle. Rejecting...")

                rejection_time = datetime.now()

                # Copy booking into history
                cursor.execute("""
                    INSERT INTO user_history
                    (booking_id, user_id, vehicle_id,
                     start_date, end_date,
                     booking_time, confirmation_time, return_time, total_amount, status)
                    SELECT booking_id, user_id, vehicle_id,
                           start_date, end_date,
                           booking_time, %s, NULL, total_amount, 'Rejected'
                    FROM bookings WHERE booking_id=%s
                """, (rejection_time, pb_booking_id))

                # Delete booking
                cursor.execute("DELETE FROM bookings WHERE booking_id=%s", (pb_booking_id,))

                conn.commit()

                # Send rejection mail
                send_booking_reject_mail(
                    pb_email, pb_booking_id, vehicle_id,
                    vtype, model, pb_start, pb_end, pb_total
                )

                print(f"Rejection mail sent to {pb_email}")

    print("\nBooking Accepted Successfully")

    cursor.close()
    conn.close()




def reject_booking():

    conn = get_connection()
    if conn is None:
        print("Database connection failed")
        return

    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT b.booking_id, b.user_id, u.name, u.address,
                   b.vehicle_id, v.type, v.model, b.total_amount
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            WHERE b.status='Pending'
        """)
        bookings = cursor.fetchall()

        if not bookings:
            print("No bookings to reject")
            return

        print("\n--- PENDING BOOKINGS ---")
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

        booking_id = input("Enter Booking ID to REJECT: ")

        cursor.execute("""
            SELECT user_id, vehicle_id, start_date, end_date, total_amount, booking_time
            FROM bookings WHERE booking_id=%s
        """, (booking_id,))
        data = cursor.fetchone()

        if data is None:
            print("Invalid Booking ID")
            return

        user_id, vehicle_id, start_date, end_date, total_amount, booking_time = data

        # user details
        cursor.execute("SELECT name, email FROM users WHERE user_id=%s", (user_id,))
        user_name, email = cursor.fetchone()

        # vehicle details
        cursor.execute("""
            SELECT type, model
            FROM vehicles WHERE vehicle_id=%s
        """, (vehicle_id,))
        vtype, model = cursor.fetchone()

        rejection_time = datetime.now()

        # Copy booking into history
        cursor.execute("""
            INSERT INTO user_history
            (booking_id, user_id, vehicle_id,
             start_date, end_date,
             booking_time, confirmation_time, return_time, total_amount, status)
            SELECT booking_id, user_id, vehicle_id,
                   start_date, end_date,
                   booking_time, %s, NULL, total_amount, 'Rejected'
            FROM bookings WHERE booking_id=%s
        """, (rejection_time, booking_id))

        # Delete booking
        cursor.execute("""
            DELETE FROM bookings WHERE booking_id=%s
        """, (booking_id,))

        conn.commit()

        # Send mail
        send_booking_reject_mail(email, booking_id, vehicle_id, vtype, model, start_date, end_date, total_amount)

        print("Booking Rejected, Stored & Removed")

    finally:
        cursor.close()
        conn.close()


def confirm_booking():

    while True:
        print("\n--- BOOKING MANAGEMENT ---")
        print("1. Accept Booking")
        print("2. Reject Booking")
        print("3. Back")

        choice = input("Enter choice: ")

        match choice:
            case "1":
                accept_booking()
            case "2":
                reject_booking()
            case "3":
                break
            case _:
                print("Invalid choice")
