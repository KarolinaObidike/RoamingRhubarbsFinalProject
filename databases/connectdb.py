import psycopg2
import os
from dotenv import load_dotenv


# Loads the Environment variables
load_dotenv()

host_name = os.environ.get("POSTGRES_HOST")
database_name = os.environ.get("POSTGRES_DB")
user_name = os.environ.get("POSTGRES_USER")
user_password = os.environ.get("POSTGRES_PASSWORD")
port = int(os.getenv("POSTGRES_PORT", 5432))




# Uses the environment variables to connect to the DB
def get_connection():

    connection = psycopg2.connect(
        host=host_name,
        dbname=database_name,
        user=user_name,
        password=user_password,
        port = port
    )

    return connection

