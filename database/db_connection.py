import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
from __init__ import get_logger

logger = get_logger(__name__)

env_path = Path(__file__).parent.parent / ".env"

if env_path.exists():
    load_dotenv(env_path)
    logger.info("env file loaded successfully")
else:
    logger.error(f".env file not found at: {env_path}")


class DatabaseConnection:

    @staticmethod
    def get_connection():

        required = {
            "PG_DATABASE": os.getenv("PG_DATABASE"),
            "PG_USER":     os.getenv("PG_USER"),
            "PG_PASSWORD": os.getenv("PG_PASSWORD"),
            "PG_HOST":     os.getenv("PG_HOST"),
            "PG_PORT":     os.getenv("PG_PORT"),
        }

        missing = [key for key, val in required.items() if not val]
        if missing:
            logger.error(f"Missing environment variables: {missing}")
            raise EnvironmentError(f"Missing environment variables: {missing}")

        try:
            conn = psycopg2.connect(
                database=required["PG_DATABASE"],
                user=required["PG_USER"],
                password=required["PG_PASSWORD"],
                host=required["PG_HOST"],
                port=required["PG_PORT"],
            )
            logger.info("Database connection established successfully")
            return conn

        except psycopg2.OperationalError as e:
            logger.error(f"Failed to connect to database: {e}")
            raise