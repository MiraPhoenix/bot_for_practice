import os
import psycopg2
import dotenv

dotenv.load_dotenv()

def create_db_connection():
    dbname = os.getenv('DB_NAME')
    dbuser = os.getenv('DB_USER')
    dbpassword = os.getenv('DB_PASSWORD')
    dbhost = os.getenv('DB_HOST')
    dbport = os.getenv('DB_PORT')

    connection = psycopg2.connect(
        dbname=dbname,
        user=dbuser,
        password=dbpassword,
        host=dbhost,
        port=dbport
    )
    return connection

def add_vacancy_to_db(connection, company, title, location, salary, skills, link):
    with connection.cursor() as cursor:
        cursor.execute("""
        INSERT INTO vacancies (company, vacancy, location, salary, skills, link)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """, (company, title, location, salary, skills, link))
        connection.commit()
        return cursor.fetchone()[0]
