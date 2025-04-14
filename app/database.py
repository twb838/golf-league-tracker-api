from typing import Any
from mysql.connector import pooling
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    raise ImportError(
        "PyMySQL is required. Please install it using: pip install pymysql"
    )

# Load environment variables
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Database:
    def __init__(self):
        self._db_config = {
            "host": os.getenv("DATABASE_HOST"),
            "port": int(os.getenv("DATABASE_PORT", 3306)),
            "user": os.getenv("DATABASE_USER"),
            "password": os.getenv("DATABASE_PASSWORD"),
            "database": os.getenv("DATABASE_NAME")
        }
        self._connection_pool = pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=20,
            pool_reset_session=True,
            **self._db_config
        )

    def execute_query(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self._connection_pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def execute_non_query(self, query: str, params: tuple = ()) -> int:
        with self._connection_pool.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                connection.commit()
                return cursor.lastrowid

db = Database()