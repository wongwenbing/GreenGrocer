import pymysql
import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = int(os.getenv("DATABASE_PORT"))
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

DATABASE_NAME = os.getenv("DATABASE_NAME")

DATABASE_CHARSET = os.getenv("DATABASE_CHARSET")
CONNECT_TIMEOUT = int(os.getenv("CONNECT_TIMEOUT", 10))  # Default to 10 seconds
READ_TIMEOUT = int(os.getenv("READ_TIMEOUT", 10))
WRITE_TIMEOUT = int(os.getenv("WRITE_TIMEOUT", 10))

def db_connector():
    db = pymysql.connect(
        charset=DATABASE_CHARSET,
        connect_timeout=CONNECT_TIMEOUT,
        cursorclass=pymysql.cursors.DictCursor,
        db=DATABASE_NAME,
        host=DATABASE_HOST,
        password=DATABASE_PASSWORD,
        read_timeout=READ_TIMEOUT,
        port=DATABASE_PORT,
        user=DATABASE_USER,
        write_timeout=WRITE_TIMEOUT,
    )
    cursor = db.cursor()
    return db, cursor