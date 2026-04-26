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

    query = """
    SELECT session.speakerName, session.sessionTitle, room.roomName
    FROM session
    JOIN room ON session.roomID = room.roomID
    WHERE session.speakerName LIKE %s
    """
    
    cursor.execute(query, ("%" + search + "%",))
    results = cursor.fetchall()

    if len(results) == 0:
        print("No speakers match search string")
    else:
        for row in results:
            print(f"Speaker: {row[0]}")
            print(f"Session: {row[1]}")
            print(f"Room: {row[2]}")
            print("-----------------------")
        
    cursor.close()
    conn.close()
# Option 2
def view_attendees_by_company():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    while True:
        company_id = input("Enter company ID: ")

        if not company_id.isdigit():
            print("Invalid company ID")
            continue

        company_id = int(company_id)

        if company_id <= 0:
            print("Invalid company ID")
            continue

        cursor.execute("SELECT * FROM company WHERE company WHERE companyID = %s", (company_id))
        company = cursor.fetchone()

        if company is None:
            print("Company does not exist")
            continue

        query = """
        SELECT attendee.attendeeName, attendee.attendeeDOB,
               session.sessionTitle, session.speakerName, room.roomName
        FROM attendee
        JOIN registration ON attendee.attendeeID = registration.attendeeID
        JOIN session ON registration.sessionID = session.sessionID
        JOIN room ON session.roomID = room.roomID
        WHERE attendee.attendeeCompanyID = %s
        """

        cursor.execute(query, (company_id,))
        results = cursor.fetchall()

        if len(results) == 0:
            print("No attendee found for for this company")
            continue

        print(f"\nCompany ID: {company_id}")

        for row in results:
            print(f"Name: {row[0]}")
            print(f"DOB: {row[1]}")
            print(f"Session: {row[2]}")
            print(f"Speaker: {row[3]}")
            print(f"Room: {row[4]}")
            print("----------------------")

        break

    cursor.close()
    conn.close()

# Option 3
def add_new_attendee():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    try:
        attendee_id = input("Enter attendee ID: ")

        if not attendee_id.isdigit():
            print("Invalid Attendee ID")
            return
        
        attendee_id = int(attendee_id)

        cursor.execute("SELECT * FROM attendees WHERE attendeeID = %s", (attendee_id,))
        if cursor.fetchone() is not None:
            print("Attendee ID already exists")
            return
        
        name = input("Enter name: ")
        dob = input("Enter DOB (YYYY-MM-DD): ")
        gender = input("Enter gender (Male/Female): ").upper()
        company_id = input("Enter company ID: ")

        if gender not in ["Male", "Female"]:
            print("Invalid gender")
            return
        
        if company_id.isdigit():
            print("Invalid Company ID")
            return
        
        company_id = int(company_id)

        cursor.execute("SELECT * FROM companies WHERE companyID = %s", (company_id,))
        if cursor.fetchone() is None:
            print("Invalid Company ID")
            return
        
        query = """
        INSERT INTO attendee (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (attendee_id, name, dob, gender, company_id))
        conn.commit()

        print("Attendee successfully added")

    except Exception as e:
        print(e)

    finally:
        cursor.close()
        conn.close()

# Option 4
def view_connected_attendees():
    attendee_id = input("Enter attendee ID: ")

    if not attendee_id.isdigit():
        print("Invalid Attendee ID")
        return
    
    attendee_id = int(attendee_id)

    # Check in MySQL
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendee WHERE attendeeID = %s", (attendee_id,))
    if cursor.fetchone() is None:
        print("Attendee does not exist")
        cursor.close()
        return
    
    cursor.close()
    conn.close()

    # Neo4j
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run("""
                MATCH (a:Attendee {attendeeID: $id})-[:CONNECTED_TO]-(b)
                 RETURN b.attendeeID AS connectedID
        """, id=attendee_id)

        records = list(result)

        if len(records) == 0:
            print("No connections found")
        else:
            print("Connected Attendees: ")
            for record in records:
                print(record["connectedID"])

    driver.close()

# Option 5
def add_attendee_connection():
    id1 = input("Enter first attendee ID: ")
    id2 = input("Enter second attendee ID: ")

    if not id1.isdigit() or not id2.isdigit():
        print("Invalid Attendee ID")
        return
    
    id1 = int(id1)
    id2 = int(id2)

    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendee WHERE attendeeID = %s", (id1,))
    if cursor.fetchone() is None:
        print("First attendee does not exist")
        cursor.close()
        conn.close()
        return
    
    cursor.execute("SELECT * FROM attendee WHERE attendeeID = %s", (id2,))
    if cursor.fetchone() is None:
        print("Second attendee does not exist")
        cursor.close()
        conn.close()
        return
    
    cursor.close()
    conn.close()

    driver = get_neo4j_driver()
    with driver.session() as session:
        session.run("""
            MERGE (a:Attendee {attendeeID: $id1})
            MERGE (b:Attendee {attendeeID: $id2})
            MERGE (a)-[:CONNECTED_TO]-(b))
        """, id1=id1, id2=id2)

        driver.close()

        print("Connection successfully added")

# Main menu
def main():
    while True:
        print("\n===== Conference App =====")
        print("1. View Speakers & Sessions")
        print("2. View Attendees by Company")
        print("3. Add New Attendee")
        print("4. View Connected Attendees")
        print("5. Add Attendee Connection")
        print("6. View Rooms")
        print("x. Exit")

        choice = input("Enter option: ")

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
        elif choice == "x":
            print("Exiting....")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
   main()
