import smtplib
import random
from dotenv import load_dotenv
load_dotenv()
import os

def send_otp(receiver_email):

    otp = str(random.randint(100000,999999))

    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    subject = "OTP Verification"
    body = f"Your OTP is: {otp}"

    message = f"Subject:{subject}\n\n{body}"

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(sender_email,app_password)

    server.sendmail(sender_email,receiver_email,message)

    server.quit()

    return otp

 

def send_booking_init_mail(receiver_email, booking_id, vehicle_id,
                           vehicle_type, model,
                           start_date, end_date, total_amount):

    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    subject = "Booking Initiated"

    body = f"""
Hello,

Your booking has been successfully initiated.

-------- BOOKING DETAILS --------
Booking ID   : {booking_id}
Vehicle ID   : {vehicle_id}
Vehicle Type : {vehicle_type}
Vehicle Name : {model}

Start Date   : {start_date}
End Date     : {end_date}

Total Amount : Rs.{total_amount}
--------------------------------

Please visit the office for payment and confirmation.

Thank you,
rentXdrive Rentals
"""

    message = f"Subject:{subject}\n\n{body}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)

    server.sendmail(sender_email, receiver_email, message)

    server.quit()




def send_booking_confirm_mail(receiver_email, booking_id, vehicle_id,
                              vehicle_type, model,
                              start_date, end_date, total_amount):

    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    subject = "Booking Confirmed"

    body = f"""
Hello,

Your booking has been CONFIRMED.

-------- BOOKING DETAILS --------
Booking ID   : {booking_id}
Vehicle ID   : {vehicle_id}
Vehicle Type : {vehicle_type}
Vehicle Name : {model}

Start Date   : {start_date}
End Date     : {end_date}

Total Amount : Rs.{total_amount}
--------------------------------

Your vehicle is now reserved for you.

Thank you for choosing our service!
rentXdrive Rentals
"""

    message = f"Subject:{subject}\n\n{body}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)

    server.sendmail(sender_email, receiver_email, message)

    server.quit()





def send_return_mail(email, booking_id, vehicle_id, vtype, model, total_amount):

    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    subject = "Vehicle Return Confirmation"

    body = f"""
Hello,

Your vehicle has been successfully returned.

Booking ID   : {booking_id}
Vehicle ID   : {vehicle_id}
Vehicle Type : {vtype}
Vehicle Name : {model}
Total Amount : {total_amount}

Thank you for choosing our service!

rentXdrive Rentals
"""

    message = f"Subject:{subject}\n\n{body}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, email, message)
    server.quit()





def send_booking_reject_mail(email, booking_id, vehicle_id, vtype, model, start_date, end_date, total_amount):

    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    subject = "Booking Rejected - Vehicle Rental System"

    body = f"""
Hello,

We regret to inform you that your booking request has been REJECTED.

Booking Details:
Booking ID   : {booking_id}
Start Date   : {start_date}
End Date     : {end_date}

Vehicle Details:
Vehicle ID   : {vehicle_id}
Vehicle Type : {vtype}
Vehicle Name : {model}

Payment Details:
Total Amount : {total_amount}

Unfortunately, this vehicle is not available or the request could not be processed.
We sincerely apologize for the inconvenience caused.
You may try booking another vehicle.

Thank you for your understanding.

rentXdrive Rentals
"""

    message = f"Subject:{subject}\n\n{body}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, email, message)
        server.quit()

        print("Rejection email sent successfully")

    except Exception as e:
        print("Error sending rejection email:", e)




def send_vehicle_change_mail(email, booking_id, old_vehicle_id, new_vehicle_id, vtype, model, start_date, end_date, total_amount):

    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")

    subject = "Vehicle Reassigned - Booking Update"

    body = f"""
Hello,

Your originally booked vehicle is no longer available for the selected dates.

Booking Details:
Booking ID        : {booking_id}
Start Date        : {start_date}
End Date          : {end_date}

Previous Vehicle:
Vehicle ID        : {old_vehicle_id}

New Vehicle Assigned:
Vehicle ID        : {new_vehicle_id}
Vehicle Type      : {vtype}
Vehicle Model     : {model}

Total Amount   : {total_amount}

We have allocated a different vehicle of the SAME type and model for your convenience.

Thank you for your understanding.

rentXdrive Rentals
"""

    message = f"Subject:{subject}\n\n{body}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, email, message)
    server.quit()