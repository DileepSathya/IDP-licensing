import bcrypt
import psycopg2
from database import db_connection
from __init__ import get_logger

logger = get_logger(__name__)


class signin_validation:

    @staticmethod
    def validate(email, password):
        logger.info("Attempting to connect to database")

        conn = db_connection.DatabaseConnection.get_connection()
        cursor = conn.cursor()
        logger.info("Database connection established")

        try:
            sql = """
                SELECT email, password_hash, user_id FROM users
                WHERE email = %s;
            """
            cursor.execute(sql, (email,))  # must be a tuple, not a bare string
            row = cursor.fetchone()

            if row is None:
                logger.warning(f"No account found for email: {email}")
                raise ValueError("No account found with this email.")

            db_email, password_hash,user_id = row


            logger.info("account found")

            # bcrypt expects bytes
            if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
                logger.warning("Invalid password attempt")
                raise ValueError("Incorrect password.")

            logger.info("User validated successfully")
            return user_id

        except ValueError:
            raise

        except Exception as e:
            logger.exception(f"Unexpected error during validation: {e}")
            raise

        finally:
            cursor.close()
            conn.close()