import user_auth 
import admin_auth
import admin_module
import user_module

while True:
    print("\n-----rentXdrive Rentals-----")
    print("1 Login as User")
    print("2 Login as Admin")
    print("3 Exit")

    choice = input("Enter choice: ")

    match choice:

        case "1":
            while True:
                print("\n-----rentXdrive Rentals-----")
                print("1 Sign Up")
                print("2 Sign In")
                print("3 Back")

                ch = input("Enter choice: ")

                match ch:
                    case "1":
                        user_auth.signup()

                    case "2":
                        user_id = user_auth.signin()   

                        if user_id:   
                            user_module.user_panel(user_id)

                    case "3":
                        break

                    case _:
                        print("Invalid choice!")

        case "2":
            if admin_auth.admin_login():
                admin_module.admin_panel()

        case "3":
            break

        case _:
            print("Invalid choice!")