import mysql.connector

db = mysql.connector.connect(
    host= '',
    user = '',
    passwd = '',
    database = ''
)

cursor = db.cursor()
