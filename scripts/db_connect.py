import pyodbc
import pandas as pd
import psycopg2

def db_connection():
    # server = 'LAPTOP-R54801RN\\MSSQLSERVER01'  # Обратите внимание на двойной слэш
    # database = 'autizm'

    # connection_string = (
    #     'DRIVER={ODBC Driver 17 for SQL Server};'
    #     f'SERVER={server};'
    #     f'DATABASE={database};'
    #     'Trusted_Connection=yes;'
    # )

    # connection = pyodbc.connect(connection_string)

    connection = psycopg2.connect(
        dbname="autizm",
        user="postgres",
        password = '44045505',
        host="localhost",
        port="5432",
    )

    return connection

def query(query):

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    records = cursor.fetchall()

    info_list = []
    for row in records:
        row_list = []
        for collumn in row:
            row_list.append(str(collumn))
        info_list.append(row_list)
    
    conn.close()
    return pd.DataFrame(info_list, columns=columns)
