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


## Notes
- This project was tested on the VM before submission
- MySQL and Neo4j must be running before executing the program.

## Author
Name: Aiswaria Lajan