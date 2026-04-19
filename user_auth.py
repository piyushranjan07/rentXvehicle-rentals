import uuid
from database import get_connection
from mail_service import send_otp
 

def signup():

    name = input("Enter Name: ")
    dlno = input("Enter DL Number: ")
    email = input("Enter Email: ")
    password = input("Enter Password: ")
    phone = input("Enter Phone: ")
    address = input("Enter Address: ")

    otp = send_otp(email)

    attempts = 3

    while attempts > 0:
        user_otp = input("Enter OTP sent to email: ")

        if otp == user_otp:
            break
        else:
            attempts -= 1
            print(f"Incorrect OTP. Attempts left: {attempts}")

    if attempts == 0:
        print("OTP Verification Failed")
        return

    user_id = str(uuid.uuid4()).replace("-", "")[:10]

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (user_id, name, dlno, email, password, phone, address))
    conn.commit()

    print("Signup Successful")

    cursor.close()
    conn.close()


def signin():

    email = input("Enter Email: ")
    password = input("Enter Password: ")

    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))

    user = cursor.fetchone()

    if user is None:
        print("Invalid Credentials")
        cursor.close()
        conn.close()
        return False

    otp = send_otp(email)

    attempts = 3

    while attempts > 0:
        user_otp = input("Enter OTP: ")

        if otp == user_otp:
            print("Login Successful")
            cursor.close()
            conn.close()
            return user[0]
        else:
            attempts -= 1
            print(f"Incorrect OTP. Attempts left: {attempts}")

    print("Incorrect OTP. Login failed")

    cursor.close()
    conn.close()
    return None