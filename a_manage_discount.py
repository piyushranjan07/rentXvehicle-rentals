from database import get_connection

 
def add_update_discount():

    conn = get_connection()
    cursor = conn.cursor()

    print("\nApply Discount By:")
    print("1. Vehicle ID")
    print("2. Vehicle Type")
    print("3. Vehicle Model")

    choice = input("Enter choice: ")

    if choice == "1":

        vid = input("Enter Vehicle ID: ")
        discount = float(input("Enter Discount: "))

        cursor.execute(
            "UPDATE vehicles SET discount=%s WHERE vehicle_id=%s",
            (discount, vid)
        )

    elif choice == "2":

        # Show all available vehicle types
        cursor.execute("SELECT DISTINCT type FROM vehicles")
        types = cursor.fetchall()

        print("\nAvailable Vehicle Types:")
        for t in types:
            print("-", t[0])

        vtype = input("Enter Vehicle Type: ")
        discount = float(input("Enter Discount: "))

        cursor.execute(
            "UPDATE vehicles SET discount=%s WHERE type=%s",
            (discount, vtype)
        )

    elif choice == "3":

        # Show all available models
        cursor.execute("SELECT DISTINCT model FROM vehicles")
        models = cursor.fetchall()

        print("\nAvailable Vehicle Models:")
        for m in models:
            print("-", m[0])

        model = input("Enter Vehicle Model: ")
        discount = float(input("Enter Discount: "))

        cursor.execute(
            "UPDATE vehicles SET discount=%s WHERE model=%s",
            (discount, model)
        )

    else:
        print("Invalid Choice")
        return

    conn.commit()

    print(f"Discount Applied Successfully to {cursor.rowcount} vehicle(s)")

    cursor.close()
    conn.close()


def remove_discount():

    conn = get_connection()
    cursor = conn.cursor()

    print("\nRemove Discount By:")
    print("1. Vehicle ID")
    print("2. Vehicle Type")
    print("3. Vehicle Model")

    choice = input("Enter choice: ")

    if choice == "1":

        vid = input("Enter Vehicle ID: ")

        cursor.execute(
            "UPDATE vehicles SET discount=0 WHERE vehicle_id=%s",
            (vid,)
        )

    elif choice == "2":

        cursor.execute("SELECT DISTINCT type FROM vehicles")
        types = cursor.fetchall()

        print("\nAvailable Vehicle Types:")
        for t in types:
            print("-", t[0])

        vtype = input("Enter Vehicle Type: ")

        cursor.execute(
            "UPDATE vehicles SET discount=0 WHERE type=%s",
            (vtype,)
        )

    elif choice == "3":

        cursor.execute("SELECT DISTINCT model FROM vehicles")
        models = cursor.fetchall()

        print("\nAvailable Vehicle Models:")
        for m in models:
            print("-", m[0])

        model = input("Enter Vehicle Model: ")

        cursor.execute(
            "UPDATE vehicles SET discount=0 WHERE model=%s",
            (model,)
        )

    else:
        print("Invalid Choice")
        return

    conn.commit()

    print(f"Discount Removed from {cursor.rowcount} vehicle(s)")

    cursor.close()
    conn.close()

def discount_menu():

    while True:
        print("\n--- DISCOUNT MANAGEMENT ---")
        print("1. Add/Update Discount")
        print("2. Remove Discount")
        print("3. Back")

        choice = input("Enter choice: ")

        match choice:
            case "1": add_update_discount()
            case "2": remove_discount()
            case "3": break
            case _: print("Invalid Choice")