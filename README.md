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



## Features
1. View Speakers and Sessions
2. View Attendees by Company
3. Add New Attendees
4. View Connected Attendees
5. Add Attendee Connection
6. View Rooms

## How to Run the Project

### Step 1: Install Required Packages
Run the following commands:

pip install mysql-connector-python
pip install neo4j

### Step 2: Setup Databases
This project is designed to run on VM

#### MySQL
- Import the file: appdbproj.sql
- Database name: appdbproj

#### Neo4j
- Import the file: adddbprojNeo4j.json
- Database name: appdbprojNeo4j

### Step 3: Run the Application

python main.py

## Notes
- This project was tested on the VM before submission
- MySQL and Neo4j must be running before executing the program.

## Author
Name: Aiswaria Lajan