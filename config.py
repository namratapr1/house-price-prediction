import pymysql

def get_db_connection():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="namrata123",   # your MySQL password
        database="House_db",        # FIXED: matches your SQL database name
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
