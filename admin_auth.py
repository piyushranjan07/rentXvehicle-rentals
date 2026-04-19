from mail_service import send_otp
from database import get_connection
 

def admin_login():

    email = input("Enter Admin Email: ")
    password = input("Enter Password: ")

    conn = get_connection()
    cursor = conn.cursor()

    # Check credentials from DB
    query = "SELECT * FROM admins WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))

    admin = cursor.fetchone()

    if admin is None:
        print("Invalid Admin Credentials")
        cursor.close()
        conn.close()
        return False

    # Send OTP
    # otp = send_otp(email)

    # attempts = 3

    # while attempts > 0:
    #     user_otp = input("Enter OTP: ")

    #     if otp == user_otp:
    #         print("Admin Login Successful")
    #         cursor.close()
    #         conn.close()
    #         return True
    #     else:
    #         attempts -= 1
    #         print(f"Incorrect OTP.")

    # print("Incorrect OTP. Login failed.")

    cursor.close()
    conn.close()
    # return False
    return True