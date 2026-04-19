import u_update_profile
import u_view_vehicle
import u_create_booking
import u_history
 
def user_panel(user_id):

    while True:
        print("\n----- USER PANEL -----")
        print("1. Update Profile")
        print("2. View Available Vehicles")
        print("3. Create Booking")
        print("4. Booking History")
        print("5. Exit")

        choice = input("Enter choice: ")

        match choice:
            case "1":
                u_update_profile.update_profile(user_id)

            case "2":
                u_view_vehicle.view_vehicles()

            case "3":
                u_create_booking.create_booking(user_id)

            case "4":
                u_history.booking_history(user_id)

            case "5":
                break

            case _:
                print("Invalid Choice")