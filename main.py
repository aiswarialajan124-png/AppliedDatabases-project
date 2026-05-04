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
            