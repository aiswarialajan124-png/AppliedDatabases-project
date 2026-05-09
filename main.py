import pymysql
from neo4j import GraphDatabase

# Connection helpers
def get_mysql_connection():
    return pymysql.connect(
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

#  cached room data (spec says new rooms added mid-session should not appear)
_rooms_cache = None

# option 1 – view speakers & sessions 

def view_speaker_sessions():
    name = input("Enter speaker name : ")
    print(f"Session Details For :  {name}")
    print("-" * 44)

    conn = get_mysql_connection()
    cursor = conn.cursor()

    # get speaker name, session title and room name for matching speakers
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
            # print speaker | session title | room name
            print(f"{row[0]:<22} | {row[1]:<35} | {row[2]}")

# option 2 – view attendees by company 

def view_attendees_by_company():
    while True:
        company_id = input("Enter Company ID : ")

        # must be a positive integer - keep asking if not
        if not company_id.lstrip('-').isdigit() or int(company_id) <= 0:
            continue

        company_id = int(company_id)
        conn = get_mysql_connection()
        cursor = conn.cursor()

        # check if company exists first
        cursor.execute("SELECT companyName FROM company WHERE companyID = %s", (company_id,))
        company = cursor.fetchone()

        if not company:
            # company id is valid number but doesnt exist in db
            print(f"Company with ID  {company_id}  doesn't exist")
            cursor.close()
            conn.close()
            continue

        company_name = company[0]
        print(f"{company_name}  Attendees")

        # get attendee details with session info, date and room
        # updated spec adds date as second last column
        cursor.execute("""
            SELECT a.attendeeName, a.attendeeDOB,
                   s.sessionTitle, s.speakerName, s.sessionDate, r.roomName
            FROM attendee a
            JOIN registration reg ON a.attendeeID = reg.attendeeID
            JOIN session s        ON reg.sessionID = s.sessionID
            JOIN room r           ON s.roomID = r.roomID
            WHERE a.attendeeCompanyID = %s
            ORDER BY a.attendeeName
        """, (company_id,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            # company exists but no attendees registered for any session
            print(f"No attendees found for  {company_name}")
        else:
            for row in rows:
                dob  = str(row[1])
                date = str(row[4])
                # name | dob | session title | speaker | date | room
                print(f"{row[0]:<18} | {dob} | {row[2]:<38} | {row[3]:<20} | {date} | {row[5]}")
        break

# option 3 – add new attendee 

def add_new_attendee():
    print("Add New Attendee")
    print("-" * 16)

    attendee_id = input("Attendee ID : ")
    name        = input("Name : ")
    dob         = input("DOB : ")
    gender      = input("Gender : ")
    company_id  = input("Company ID : ")

    # validate gender before touching the database
    if gender not in ("Male", "Female"):
        print("*** ERROR *** Gender must be Male/Female")
        return

    conn   = get_mysql_connection()
    cursor = conn.cursor()

    # check company exists before inserting
    try:
        cid = int(company_id)
        cursor.execute("SELECT companyID FROM company WHERE companyID = %s", (cid,))
        if not cursor.fetchone():
            print(f"*** ERROR *** Company ID: {company_id} does not exist")
            cursor.close()
            conn.close()
            return
    except ValueError:
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
        print("Attendee successfully added")

    except mysql.connector.Error as e:
        # check for duplicate attendee id (error 1062)
        if e.errno == 1062:
            print(f"*** ERROR *** Attendee ID: {attendee_id} already exists")
        else:
            # show the mysql error for invalid id, dob etc as per spec
            print(f"*** ERROR *** ({e.errno}, \"{e.msg}\")")
    finally:
        cursor.close()
        conn.close()

# option 4 – view connected attendees

def view_connected_attendees():
    while True:
        attendee_id = input("Enter Attendee ID : ")

        # must be numeric
        if not attendee_id.isdigit():
            print("*** ERROR *** Invalid attendee ID")
            continue

        attendee_id = int(attendee_id)

        # check attendee exists in mysql first
        conn   = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT attendeeName FROM attendee WHERE attendeeID = %s", (attendee_id,))
        mysql_row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not mysql_row:
            # not in mysql or neo4j
            print("*** ERROR *** Attendee does not exist")
            return

        attendee_name = mysql_row[0]
        print(f"Attendee Name:  {attendee_name}")
        print("-" * 20)

        # now check neo4j for connections
        driver = get_neo4j_driver()
        with driver.session() as neo_session:
            result = neo_session.run("""
                MATCH (a:Attendee {attendeeID: $id})-[:CONNECTED_TO]-(b:Attendee)
                RETURN b.attendeeID AS connID
            """, id=attendee_id)
            connected_ids = [record["connID"] for record in result]
        driver.close()

        if not connected_ids:
            # in mysql but not in neo4j or no connections
            print("No connections")
            return

        # look up the name of each connected attendee from mysql
        conn   = get_mysql_connection()
        cursor = conn.cursor()
        print("These attendees are connected:")
        for cid in connected_ids:
            cursor.execute("SELECT attendeeName FROM attendee WHERE attendeeID = %s", (cid,))
            row = cursor.fetchone()
            cname = row[0] if row else "(unknown)"
            print(f"{cid:<6} | {cname}")
        cursor.close()
        conn.close()
        return

# option 5 – add attendee connection 

def add_attendee_connection():
    while True:
        id1 = input("Enter Attendee 1 ID : ")
        id2 = input("Enter Attendee 2 ID : ")

        # both must be numeric
        if not id1.isdigit() or not id2.isdigit():
            print("*** ERROR *** Attendee IDs must be numbers")
            continue

        id1, id2 = int(id1), int(id2)

        # attendee cannot connect to themselves
        if id1 == id2:
            print("*** ERROR *** An attendee cannot connect to him/herself")
            continue

        # verify both attendees exist in mysql
        # if either doesnt exist we should not create neo4j nodes
        conn   = get_mysql_connection()
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

        # check if already connected in neo4j (either direction)
        driver = get_neo4j_driver()
        with driver.session() as neo_session:
            check = neo_session.run("""
                MATCH (a:Attendee {attendeeID: $id1})-[:CONNECTED_TO]-(b:Attendee {attendeeID: $id2})
                RETURN count(*) AS cnt
            """, id1=id1, id2=id2)
            already = check.single()["cnt"] > 0

            if already:
                driver.close()
                print("*** ERROR *** These attendees are already connected")
                continue

            # create the connection - use MERGE so nodes are created if not already in neo4j
            neo_session.run("""
                MERGE (a:Attendee {attendeeID: $id1})
                MERGE (b:Attendee {attendeeID: $id2})
                MERGE (a)-[:CONNECTED_TO]->(b)
            """, id1=id1, id2=id2)

        driver.close()
        print(f"Attendee {id1} is now connected to Attendee {id2}")
        return

# option 6 – view rooms (cached on first call)

def view_rooms():
    global _rooms_cache

    # only fetch from db once - new rooms added after wont show until restart
    if _rooms_cache is None:
        conn   = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT roomID, roomName, capacity FROM room ORDER BY roomID")
        _rooms_cache = cursor.fetchall()
        cursor.close()
        conn.close()

    print(f"{'RoomID':<8} | {'RoomName':<20} | Capacity")
    for row in _rooms_cache:
        print(f"{row[0]:<8} | {row[1]:<20} | {row[2]}")

# main menu
def main():
    while True:
        print("\nConference Management")
        print("--------------------")
        print("\nMENU")
        print("====")
        print("1 - View Speakers & Sessions")
        print("2 - View Attendees by Company")
        print("3 - Add New Attendee")
        print("4 - View Connected Attendees")
        print("5 - Add Attendee Connection")
        print("6 - View Rooms")
        print("x - Exit application")
        choice = input("Choice: ")

        if   choice == "1": view_speaker_sessions()
        elif choice == "2": view_attendees_by_company()
        elif choice == "3": add_new_attendee()
        elif choice == "4": view_connected_attendees()
        elif choice == "5": add_attendee_connection()
        elif choice == "6": view_rooms()
        elif choice == "x": break
        # anything else - show menu again

if __name__ == "__main__":
    main()