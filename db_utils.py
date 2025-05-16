import pymysql

def run_query(query):
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",         
            password="Raj@123", 
            database="federal_register",   
            cursorclass=pymysql.cursors.Cursor
        )

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                cursor.description = cursor.description  # Needed for headers
                return cursor  # Return full cursor (with .fetchall and .description)
    except Exception as e:
        raise RuntimeError(f"MySQL query failed: {e}")
