# Applied Databases Project

## Overview
This is a comand-line conference management application built in Python for the Applied Databases module.

It uses two different types of databases working together -  a **MySQL** relational database to store attendee, company, session and room data, and a **Neo4j** graph database to store and query connections between attendees.

The application was developed and tested on the ATU Virtual Machine.

## Database Used

### MySQL - 'appdbproj'
A relational database containing the following tables:
- 'company' - companies that attendees belong to 
- 'attendee' - conference attendees and their details
- 'session' - conference sessions with speaker, date and room
- 'room' - rooms where sessions are held
- 'registration' - records of which attendees attended which sessions.

### Neo4j - 'appdbprojNeo4j'
A graph database storing 'Attendee' nodes and 'CONNECTED_TO' relationships between them. The direction of the relationship does not matter - if A is connected to B, B is also connected to A.

## Setup Instructions

### 1: Install Required Packages
```bash
pip install mypysql neo4j cryptography
```
**Note:** This project uses `pymysql` instead of `mysql-connector-pyhton`. The standard mysql-connector package (version 9.6) crashes silently on some systems, so pymysql was used as a reliable alternative. The `cryptography` package is required for MySQL SHA256 password authentication.

### 2: Set up MySQL
- Open MySQL Workbench
- Run `appdbproj.sql` to create and populate the database.

### 3: Set up Neo4j
- Open Neo4j browser at `http://localhost:7474`
- Make sure you are connected to the `appdbprojNeo4j` database
- Run the Cypher statements from `appdbprojNeo4j.json` to create the attendee nodes and relationships

### 4: Run the Application
Make sure both MySQL and Neo4j are running, then:
```bash
python main.py
```

## Menu Options
```
1 - View Speakers & Sessions
2 - View Attendees by Company
3 - Add New Attendee
4 - View Connected Attendees
5 - Add Attendee Connection
6 - View Rooms
x - Exit application
```

### Option 1 - View Speakers & Sessions
Enter a speakers name or part of a name. The app searches the MySQL session table using a LIKE query and returns all matching speakers along with their sessions on title and room name.

### Option 2 - View Attendees by Company
Enter a company ID to see all attendees registrated from that company. For each attendee it shows their name, date of birth, session title, speaker name, session date and room. The company ID must be a positive number - invalid inputs are rejected and the user is asked again.

### Option 3 - Add New Attendee
Prompts the user to enter a new attendee's detail (ID, name, date of birth, gender, and company ID) and inserts them into the MySQL attendee table. The following are validated before inserting:
- Gender must be Male or Female
- Company ID must exist in the database
- Attendee ID must not already exist

### Option 4 - View Connected Attendees
Enter an attendee ID to see who they are connected to in the Neo4j graph database. The app first checks MySQL to confirm the attendee exists, then queries Neo4j for any CONNECTED_TO relationships in either direction. If the attendee has no connections it shows "No connections".

### Option 5 - Add Attendee Connection
Enter two attendee IDs to create a CONNECTED_TO relationship between them in Neo4j. Before creating the connection the app checks:
- Both IDs must be numbers
- An attendee cannot connect to themselves
- Both attendees must exist in MySQL
- They must not already be connected

If an attendee exists in MySQL but not yet in Neo4j, the node is created automatically using MERGE.

### Option 6 - View Rooms
Displays all rooms in the system with their ID, name and capacity. Room data is loaded from MySQL on the first call and cached for the rest of the session -  any rooms added to the database while the application is running will not appear until it is restarted.

## Project Structure
```
AppliedDatabases-project/
|── appdbproj.sql
|── appdbprojNeo4j.json
|── GitLink.txt
|── Innovation Document.pdf
|── main.py
|── README.md
└── test.py
```

## Notes
- All testing was done on the ATU Virtual Machine

- MySQL and Neo4j must both be running before starting the application

## Author
Name: Aiswaria Lajan