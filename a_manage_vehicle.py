from database import get_connection
 
def view_vehicles():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT type FROM vehicles")
    types = cursor.fetchall()

    if not types:
        print("No vehicles found")
        return

    type_list = [t[0] for t in types]

    print("\n---AVAILABLE TYPES OF VEHICLES ---")
    print("1. All Types")

    for i, t in enumerate(type_list, start=2):
        print(f"{i}. {t}")

    print(f"{len(type_list)+2}. Back")

    choice = input("Enter choice: ")

    if not choice.isdigit():
        print("Invalid input")
        return

    choice = int(choice)

    if choice == 1:
        cursor.execute("""
            SELECT vehicle_id, type, model, price_per_day, discount, status
            FROM vehicles
        """)

    elif choice == len(type_list) + 2:
        return

    elif choice < 1 or choice > len(type_list) + 2:
        print("Invalid choice")
        return

    else:
        selected_type = type_list[choice - 2]

        cursor.execute("""
            SELECT vehicle_id, type, model, price_per_day, discount, status
            FROM vehicles
            WHERE type=%s
        """, (selected_type,))

    vehicles = cursor.fetchall()

    if not vehicles:
        print("No vehicles found")
        return

    vehicle_list = []

    for v in vehicles:

        vid, vtype, model, price, discount, status = v

        if discount is None:
            discount = 0

        # Get average rating from user_history
        cursor.execute("""
            SELECT AVG(rating) FROM user_history
            WHERE vehicle_id=%s AND rating IS NOT NULL
        """, (vid,))
        avg_rating = cursor.fetchone()[0]

        vehicle_dict = {
            "vehicle_id": vid,
            "type": vtype,
            "model": model,
            "price_per_day": price,
            "discount": discount,
            "status": status,
            "rating": round(avg_rating, 1) if avg_rating is not None else "No Ratings"
        }

        vehicle_list.append(vehicle_dict)

    print("\n--- VEHICLES ---")
    for vehicle in vehicle_list:
        print(vehicle)

    cursor.close()
    conn.close()



def add_vehicle():

    vehicle_id = input("Enter Vehicle ID: ")
    v_type = input("Enter Type: ")
    model = input("Enter Model: ")
    price = float(input("Enter Price: "))

    discount_input = input("Enter Discount (press Enter to skip): ")

    if discount_input == "":
        discount = None   # this will go as null in database
    else:
        discount = float(discount_input)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO vehicles VALUES (%s,%s,%s,%s,%s,%s)",
        (vehicle_id, v_type, model, price, discount, "Available")
    )

    conn.commit()

    print("Vehicle Added Successfully")

    cursor.close()
    conn.close()


def delete_vehicle():

    vid = input("Enter Vehicle ID: ")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vehicles WHERE vehicle_id=%s", (vid,))
    conn.commit()

    print("Vehicle Deleted")

    cursor.close()
    conn.close()


def update_vehicle():

    vid = input("Enter Vehicle ID: ")
    price = float(input("Enter New Price: "))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE vehicles SET price_per_day=%s WHERE vehicle_id=%s",
        (price, vid)
    )

    conn.commit()
    print("Vehicle Updated")

    cursor.close()
    conn.close()


def view_vehicle_usage():

    vid = input("Enter Vehicle ID: ")

    conn = get_connection()
    cursor = conn.cursor()

    # Get vehicle info
    cursor.execute("""
        SELECT type, model FROM vehicles WHERE vehicle_id=%s
    """, (vid,))
    data = cursor.fetchone()

    if data is None:
        print("Invalid Vehicle ID")
        cursor.close()
        conn.close()
        return

    vtype, model = data

    # Total confirmed bookings = currently active + completed
    cursor.execute("""
        SELECT COUNT(*) FROM bookings WHERE vehicle_id=%s AND status='Booked'
    """, (vid,))
    active_bookings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM user_history WHERE vehicle_id=%s AND status='Completed'
    """, (vid,))
    completed_bookings = cursor.fetchone()[0]

    total_bookings = active_bookings + completed_bookings

    # Total revenue = active bookings + completed rentals
    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0) FROM bookings WHERE vehicle_id=%s AND status='Booked'
    """, (vid,))
    active_revenue = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(total_amount), 0) FROM user_history WHERE vehicle_id=%s AND status='Completed'
    """, (vid,))
    completed_revenue = cursor.fetchone()[0]

    total_revenue = active_revenue + completed_revenue

    print(f"\n--- VEHICLE USAGE: {vid} ---")
    print(f"  Type              : {vtype}")
    print(f"  Model             : {model}")
    print(f"  Total Bookings    : {total_bookings}")
    print(f"  Total Revenue     : Rs.{total_revenue}")
    print("-------------------------------")

    cursor.close()
    conn.close()


def vehicle_menu():

    while True:
        print("\n--- VEHICLE MANAGEMENT ---")
        print("1. View Vehicles")
        print("2. Add Vehicle")
        print("3. Delete Vehicle")
        print("4. Update Vehicle")
        print("5. View Vehicle Usage")
        print("6. Back")

        choice = input("Enter choice: ")

        match choice:
            case "1": view_vehicles()
            case "2": add_vehicle()
            case "3": delete_vehicle()
            case "4": update_vehicle()
            case "5": view_vehicle_usage()
            case "6": break
            case _: print("Invalid Choice")