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

# Option 3: Add new Attendee
def add_new_attendee():
    print("Add New Attendee")
    print("-" * 16)

    attendee_id = input("Attendee ID: ")
    name = input("Name: ")
    dob = input("DOB: ")
    gender = input("Gender: ")
    company_id = input("Company ID: ")

    # Validate gender
    if gender not in ("Male", "Female"):
        print("*** ERROR *** Gender must be Male/Female")
        return

    conn = get_mysql_connection()
    cursor = conn.cursor()

    # Check company exists
    try:
        cursor.execute("SELECT companyID FROM company WHERE companyID = %s", (int(company_id),))
    except Exception:
        print("***ERROR *** Company ID: {company_id} does not exist")
        cursor.close()
        conn.close()
        return
    
    if not cursor.fetchone():
        print(f"*** ERROR *** Company ID: {company_id} does not exist")
        cursor.close()
        conn.close()
        return
    
    try:
        cursor.execute("""
            INSERT INTO attendee 
                (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
            VALUES (%s, %s, %s, %s, %s)
        """, (attendee_id, name, dob, gender, company_id))
        conn.commit()
        print("Attendee added successfully")
    except mysql.connector.Error as e:
        # surface the MySQL error code  + message exactly as the spec shows
        print(f"*** ERROR *** ({e.errno}, \"{e.msg}\")")
    finally:
        cursor.close()
        conn.close()

# Option 4: View connected attendees
def view_connected_attendees():
    while True:
        attendee_id = input("Enter Attendee ID: ")
        if not attendee_id.isdigit():
            print("*** ERROR *** Invalid attendee ID")
            continue

        attendee_id = int(attendee_id)

        # look up name in MySQL first
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT attendeeName FROM attendee WHERE attendeeID = %s", (attendee_id,))
        mysql_row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not mysql_row:
            print("*** ERROR *** Attendee does not exist")
            return
        
        attendee_name = mysql_row[0]
        print(f"Attendee Name: {attendee_name}")
        print("-" * 20)

        # query Neo4j for connections
        driver = get_neo4j_driver()
        with driver.session() as neo_session:
            result = neo_session.run("""
                MATCH (a:Attendee {attendeeID: $id})-[:CONNECTED_TO]-(b:Attendee)
                RETURN b.attendeeID AS connID
            """, id=attendee_id)
            connected_ids = [record["connID"] for record in result]
        driver.close()

        if not connected_ids:
            print("No connections")
            return
        
        # resolve names from MySQL
        conn = get_mysql_connection()
        cursor = conn.cursor()
        print("These attendees are connected: ")
        for cid in connected_ids:
            cursor.execute("SELECT attendeeName FROM attendee WHERE attendeeID = %s", (cid,))
            row = cursor.fetchone()
            cname = row[0] if row else "(unknown)"
            print(f"{cid:<6} | {cname}")
        cursor.close()
        conn.close()
        return
    
# Option 5: Add attendee connection
def add_attendee_connection():
    while True:
        id1 = input("Enter Attendee 1 ID: ")
        id2 = input("Enter Attendee 2 ID: ")

        if not id1.isdigit() or not id2.isdigit():
            print("*** ERROR *** Attendee IDs must be numbers")
            continue

        id1, id2 = int(id1), int(id2)

        if id1 == id2:
            print("*** ERROR *** An attendee cannot connect to him/herself")
            continue

        # verify both exist in MySQL
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute(
             "SELECT attendeeID FROM attendee WHERE attendeeID IN (%s, %s)", (id1, id2)
        )
        found = [r[0] for r in cursor.fetchall()]
        cursor.close()
        conn.close()

        if len(found) < 2:
            print("*** ERROR *** One or both attendee IDs do not exist")
            continue

        # check for existing connections in Neo4j
        driver = get_neo4j_driver()
        with driver.session() as neo_session:
            check = neo_session.run("""
                MATCH (a:Attendee {attendeeID: $id1})-[CONNECTED_TO]-(b:Attendee {attendeeID: $id2})
                RETURN count(*) AS cnt
            """, id1=id1, id2=id2)
            already = check.single()["cnt"] > 0

            if already:
                driver.close()
                print("*** ERROR *** These attendees are already connected")
                continue

            # create connection
            neo_session.run("""
                MERGE (a:Attendee {attendeeID: $id1})
                MERGE (b:Attendee {attendeeID: $id2})
                MERGE (a)-[:CONNECTED_TO]->(b)
            """, id1=id1, id2=id2)

        driver.close()
        print(f"Attendee {id1} is now connected to Attendee {id2}")
        return
    
# Option 6: View rooms (cached)
def view_rooms():
    global _rooms_cache
    if _rooms_cache is None:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT roomID, roomName, capacity FROM room ORDER BY roomID")
        _rooms_cache = cursor.fetchall()
        cursor.close()
        conn.close()

    print(f"{'RoomID':<8} | {'RoomName':<20} | Capacity")
    for row in _rooms_cache:
        print(f"{row[0]:<8} | {row[1]:<20} | {row[2]}")