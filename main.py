from neo4j import GraphDatabase
import mysql.connector

def get_mysql_connection():
    return mysql.connector.connect