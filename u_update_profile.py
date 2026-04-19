from database import get_connection
from mail_service import send_otp
 

def update_profile(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, dl_no, email, phone, address FROM users WHERE user_id=%s", (user_id,))
    user = cursor.fetchone()

    if user is None:
        print("User not found")
        return

    name, dlno, email, phone, address = user

    print("\n--- CURRENT PROFILE ---")
    print("1. Name:", name)
    print("2. DL No:", dlno)
    print("3. Phone:", phone)
    print("4. Address:", address)

 
    updates = {}

    while True:

        print("\nWhat do you want to update?")
        print("1. Name")
        print("2. DL No")
        print("3. Phone")
        print("4. Address")
        print("5. Done / Save & Exit")

        choice = input("Enter choice: ")

        match choice:
            case "1":
                updates["name"] = input("Enter New Name: ")

            case "2":
                updates["dl_no"] = input("Enter New DL No: ")

            case "3":
                updates["phone"] = input("Enter New Phone: ")

            case "4":
                updates["address"] = input("Enter New Address: ")

            case "5":
                break

            case _:
                print("Invalid choice")

    if not updates:
        print("No changes made")
        return

    otp = send_otp(email)

    for i in range(3):
        user_otp = input("Enter OTP: ")

        if user_otp == otp:

            fields = ", ".join([f"{k}=%s" for k in updates.keys()])
            values = list(updates.values())

            query = f"UPDATE users SET {fields} WHERE user_id=%s"
            values.append(user_id)

            cursor.execute(query, tuple(values))
            conn.commit()

            print("Profile Updated Successfully")
            break

        else:
            print("Incorrect OTP")

    else:
        print("Incorrect OTP. Update Cancelled")

    cursor.close()
    conn.close()