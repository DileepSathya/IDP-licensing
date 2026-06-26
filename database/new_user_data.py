from database import db_connection
from __init__ import get_logger

logger = get_logger(__name__)

class InsertNewUser:

    @staticmethod
    def new_client(fname, lname, user_type, role, email, password_hash):

        logger.info("Attempting to connect to database")

        conn = db_connection.DatabaseConnection.get_connection()
        cursor = conn.cursor()
        logger.info("Database connection established")

        try:
            logger.info("Inserting user data into database")

            sql = """
            INSERT INTO users
                (f_name, l_name, user_type, role, email, password_hash)
            VALUES
                (%s, %s, %s, %s, %s, %s)
            """
            #                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^
            #  6 columns → must have 6 placeholders (was only 5 before)

            cursor.execute(sql, (fname, lname, user_type, role, email, password_hash.decode("utf-8")))

            conn.commit()
            logger.info("User data inserted successfully")

        except Exception as e:
            conn.rollback()
            # UniqueViolation error code is 23505
            if hasattr(e, 'pgcode') and e.pgcode == '23505':
                logger.warning(f"Duplicate email attempted: {email}")
                raise ValueError("An account with this email already exists.")
            logger.exception(f"Failed to insert user: {e}")
            raise

        finally:
            cursor.close()
            conn.close()