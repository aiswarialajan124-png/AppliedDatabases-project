def main():
    while True:
        print("\n===== Conference App =====")
        print("1. View Speakers and Sessions")
        print("2. View Attendees by Company")
        print("3. Add New Attendee")
        print("4. View Connected Attendees")
        print("5. Add Attendee Connection")
        print("6. View Rooms")
        print("x. Exit")

        choice = input("Enter option: ")

        if choice == "1":
            print("Option 1 selected")
        elif choice == "x":
            print("Exiting...")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()