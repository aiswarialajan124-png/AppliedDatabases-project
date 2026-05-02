from neo4j import GraphDatabase
import mysql.connector

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="appdbproj"
    )
def get_neo4j_driver():
    return GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "neo4jneo4j")
    )

# Option 1
def view_speaker_sessions():
    search = input("Enter speaker name: ")

    conn = get_mysql_connection()
    cursor = conn.cursor()

    query = """
        SELECT session.speakerName, session.sessionTitle, room.roomName
        FROM session
        JOIN room ON session.roomID = room.roomID
        WHERE session.speakerName LIKE %s
    """

    cursor.execute(query, ("%" + search + "%",))
    results = cursor.fetchall()

    if not results:
        print("No speakers found")
    else:
        for r in results:
            print(f"Speaker: {r[0]}")
            print(f"Session: {r[1]}")
            print(f"Room: {r[2]}")
            print("---------------------")
    
    cursor.close()
    conn.close()

# Option 2
def view_attendees_by_company():
    company_id = input("Enter company ID: ")

    if not company_id.isdigit():
        print("Invalid company ID")
        return
    
    conn = get_mysql_connection()
    cursor = conn.cursor()

    query = """
        SELECT attendee.attendeeName, session.sessionTitle, session.speakerName
        FROM attendee
        JOIN registration ON attendee.attendeeID = registration.attendeeID
        JOIN session ON registration.sessionID = session.sessionID
        WHERE attendee.attendeeCompanyID = %s
    """

    cursor.execute(query, (company_id,))
    results = cursor.fetchall()

    if not results:
        print("No attendee found")
    else:
        for r in results:
            print(f"Name: {r[0]}")
            print(f"Session: {r[1]}")
            print(f"Speaker: {r[2]}")
            print("----------------------")

    cursor.close()
    cursor.close()

# Option 3
def add_new_attendee():
    try:
        attendee_id = int(input("Enter ID: "))
        name = input("Enter name: ")
        dob = input("Enter DOB (YYYY-MM-DD): ")
        gender = input("Enter gender (Male/Female): ")
        company = int(input("Enter company ID: "))

        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO attendee
            (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
            VALUES (%s, %s, %s, %s, %s)
        """, (attendee_id, name, dob, gender, company))

        conn.commit()
        print("Added succesfully")

        cursor.close()
        conn.close()

    except Exception as e:
        print(e)

# Option 4
def view_connected_attendees():
    attendee_id = input("Enter attendee ID: ")

    if not attendee_id.isdigit():
        print("Invalid ID")
        return
    
    driver = get_neo4j_driver()

    with driver.session() as session:
        result = session.run("""
            MATCH (a:Attendee {attendeeID:$id})-[:CONNECTED_TO]-(b)
            RETURN b.attendeeID AS id
        """, id=int(attendee_id))

        data = list(result)

        if not data:
            print("No connections")
        else:
            print("Connected attendees: ")
            for r in data:
                print(r["id"])
    
    driver.close()

# Option 5
def add_attendee_connection():
    id1 = input("Enter first attendee ID: ")
    id2 = input("Enter second attendee ID: ")

    if not id1.isdigit() or not id2.isdigit():
        print("Invalid ID")
        return
    
    driver = get_neo4j_driver()

    with driver.session() as session:
        session.run("""
            MERGE (a:Attendee {attendeeID:$id1})
            MERGE (b:Attendee {attendeeID:$id2})
            MERGE (a)-[:CONNECTED_TO]-(b)
        """, id1=int(id1), id2=int(id2))

    driver.close()
    print("Connection added")

# Option 6 
def view_rooms():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT roomID, roomName, capicity FROM room")
    results = cursor.fetchall()

    for r in results:
        print(f"Room ID: {r[0]}, Name: {r[1]}, Capacitry: {r[2]}")

    cursor.close()
    conn.close()

# Main menu
def main():
    while True:
        print("\nConference App")
        print("1. View Speakers & Session")
        print("2. View Attendees by Company")
        print("3. Add New Attendee")
        print("4. View Connected Attendees")
        print("5. Add Attendee Connection")
        print("6. View Rooms")
        print("x. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            view_speaker_sessions()
        elif choice == "2":
            view_attendees_by_company()
        elif choice == "3":
            add_new_attendee()
        elif choice == "4":
            view_connected_attendees()
        elif choice == "5":
            add_attendee_connection()
        elif choice == "6":
            view_rooms()
        elif choice == "x":
            print("Exiting...")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
    