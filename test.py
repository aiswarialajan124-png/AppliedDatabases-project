print("start")
import mysql.connector
print("imported")
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="appdbproj"
)
print("connected")