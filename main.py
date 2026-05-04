from neo4j import GraphDatabase
import mysql.connector

# Connection helpers
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

# Cached room data (option 6 requirement)
_rooms_cache = None

# Option 1: View Speakers and sessions
def view_speakers_and_sessionsS():
    name = input("Enter speaker name: ")
    print(f"Session Details for: {name}")
    print("-" * 44)

    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("""
            SELECT s.speakerName, s.sessionTitle, r.roomName
            FROM session s
            JOIN room r ON s.roomID = r.roomID
            WHERE s.speakerName LIKE %s
    """, ("%" + name + "%",))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    if not results:
        print("No speakers found of that name")
    else:
        for row in results:
            print(f"{row[0]:<20} | {row[1]:<35} | {row[2]}")

# Option 2: View Attendees by company
def view_attendees_by_company():
    while True:
        company_id = input("Enter company ID: ")

        # Must be a positive integer
        if not company_id.lstrip('-').isdigit() or int(company_id) <= 0:
            continue # keep asking

        company_id = int(company_id)

        conn = get_mysql_connection()
        cursor = conn.cursor()

        # check company exists
        cursor.execute("SELECT companyName FROM company WHERE companyID = %s", (company_id,))
        company = cursor.fetchone()
        if not company:
            print(f"Company with ID {company_id} doesn't exist")
            cursor.close()
            conn.close()
            continue # keep asking

        company_name = company[0]
        print(f"{company_name} Attendees")

        # fetch attendees + sessions + rooms
        cursor.execute("""
            SELECT a.attendeeName, a.attendeeDOB,
                   s.sessionTitle, s.speakerName, s.sessionDate, r.roomName
            FROM attendee a
            JOIN registration reg ON a.attendeeID = reg.attendeeID
            JOIN session s ON reg.sessionID = s.sessionID
            JOIN room r ON s.roomID = r.roomID
            WHERE a.attendeeCompanyID = %s
            ORDER BY a.attendeeName
        """, (company_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            print(f"No attendees found for {company_name}")
        else:
            for row in rows:
                dob = str(row[1])
                date = str(row[4])
                print(f"{row[0]:<18} | {dob} | {row[2]:<38} | {row[3]:<20} | {date} | {row[5]}")
                break # done