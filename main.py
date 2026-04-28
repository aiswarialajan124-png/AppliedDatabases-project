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
def view_speakers_sessions():
    search = input("Enter speaker name: ")

    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT speakerName, sessionTitle, roomName
        FROM session
        JOIN room ON session.roomID = room.roomID
        WHERE speakerName LIKE %s
    """, ("%" + search + "%",))

    results = cursor.fetchall()

    if not results:
        print("No speakers found")
    else:
        for r in results:
           print(r)

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

    cursor.execute("""
            SELECT attendeeName, sessionTitle, speakerName
            FROM attendee
            JOIN registration ON attendee.attendeeID = registration.attendeeID
            JOIN session ON registration.sessionID = session.sessionID
            WHERE attendeeCompanyID = %s
    """, (company_id,))

    results = cursor.fetchall()

    if not results:
        print("No attendees found")
    else:
        for r in results:
            print(r)

    cursor.close()
    conn.close()

# Option 3
def add_new_attendee():
    try:
        id = int(input("Enter ID: "))
        name = input("Enter name: ")
        dob = input("Enter DOB (YYYY-MM-DD): ")
        gender = input("Enter gender (Male/Female): ")
        company = int(input("Enter company ID: "))

        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO attendee
            VALUES (%s, %s, %s, %s, %s)
        """, (id, name, dob, gender, company))
        
        conn.commit()
        print("Added successfully")

        cursor.close()
        conn.close()

    except Exception as e:
        print(e)

# Option 4
def view_connected_attendees():
    attendee_id = input("Enter attendee ID: ")
    
    driver = get_neo4j_driver()
    
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Attendee {attendeeID:$id})-[:CONNECTED_TO]-(b)
            RETURN b.attendeeID
        """, id=int(attendee_id))
        
        data = list(result)
        
        if not data:
            print("No connections")
        else:
            for r in data:
                print(r["b.attendeeID"])
        
    driver.close()

# Option 5
def add_attendee_connection():
    id1 = input("Enter first attendee ID: ")
    id2 = input("Enter second attendee ID: ")

    driver = get_neo4j_driver()

    with driver.session() as session:
        session.run("""
           MERGE (a:Attendee {attendeeID:$id1})
           MERGE (b:Attendee {attendeeID:$id2})
           MERGE (a)-[:CONNECTED_TO]-(b)
        """, id1=id1, id2=id2)

        driver.close()

        print("Connection added")

# Option 6 
def view_rooms():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM room")
    results = cursor.fetchall()

    for r in results:
        print(r)

    cursor.close()
    conn.close()

# Main menu
def main():
    while True:
        print("\nConference App")
        print("1. View Speakers & Sessions")
        print("2. View Attendees by Company")
        print("3. Add New Attendee")
        print("4. View Connected Attendees")
        print("5. Add Attendee Connection")
        print("6. View Rooms")
        print("x. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            view_speakers_sessions()
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
            print("Exiting....")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
   main()
