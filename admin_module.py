import a_manage_vehicle
import a_manage_user
import a_manage_discount
import a_confirm_booking
import a_return_vehicle
import a_user_history
import report
import visualise_data

def admin_panel():

    while True:
        print("\n---- ADMIN PANEL ----")
        print("1. Vehicle Management")
        print("2. Customer Management")
        print("3. Discount Management")
        print("4. Confirm Booking")
        print("5. Return Vehicle")
        print("6. User Booking History")
        print("7. Generate Report")
        print("8. Visualise Data")
        print("9. Exit")

        choice = input("Enter choice: ")

        match choice:
            case "1":
                a_manage_vehicle.vehicle_menu()

            case "2":
                a_manage_user.customer_menu()

            case "3":
                a_manage_discount.discount_menu()
            
            case "4":
                a_confirm_booking.confirm_booking()
            
            case "5":
                a_return_vehicle.return_vehicle()

            case "6":
                a_user_history.user_history_menu()

            case "7":
                report.generate_report()
            
            case "8":
                visualise_data.visualise_menu()

            case "9":
                break

            case _:
                print("Invalid Choice")