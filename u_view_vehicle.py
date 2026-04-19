from database import get_connection
 
def view_vehicles():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT type FROM vehicles WHERE status='Available'")
    types = cursor.fetchall()

    if not types:
        print("No vehicles available")
        return

    type_list = [t[0] for t in types]


    print("\n---AVAILABLE TYPES OF VEHICLES ---")
    print("1. All Types")

    for i, t in enumerate(type_list, start=2):
        print(f"{i}. {t}")

    print(f"{len(type_list)+2}. Back")

    choice = int(input("Enter choice: "))

    if choice == 1:
        cursor.execute("""
            SELECT vehicle_id, type, model, price_per_day, discount
            FROM vehicles
            WHERE status='Available'
        """)

    elif choice == len(type_list) + 2:
        return

    elif choice < 1 or choice > len(type_list) + 2:
        print("Invalid choice")
        return

    else:
        selected_type = type_list[choice - 2]

        cursor.execute("""
            SELECT vehicle_id, type, model, price_per_day, discount
            FROM vehicles
            WHERE status='Available' AND type=%s
        """, (selected_type,))

    vehicles = cursor.fetchall()

    if not vehicles:
        print("No vehicles found")
        return

    # Step 4: Process data
    vehicle_list = []

    for v in vehicles:

        vid, vtype, model, price, discount = v

        if discount is None:
            discount = 0

        final_price = price - (price * discount / 100)

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
            "price_per_day": round(final_price, 2),
            "rating": round(avg_rating, 1) if avg_rating is not None else "No Ratings"
        }

        vehicle_list.append(vehicle_dict)

    # Step 5: Show output
    print("\n--- AVAILABLE VEHICLES ---")
    for vehicle in vehicle_list:
        print(vehicle)

    cursor.close()
    conn.close()