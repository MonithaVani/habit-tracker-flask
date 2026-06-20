from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from db import mysql



def register_user(username, email, password):

    cur = mysql.connection.cursor()

    # Check if email already exists
    cur.execute(
        "SELECT * FROM users WHERE email=%s",
        (email,)
    )

    existing_user = cur.fetchone()

    if existing_user:
        return False, "Email already registered"

    hashed_password = generate_password_hash(password)

    cur.execute(
        """
        INSERT INTO users(username,email,password)
        VALUES(%s,%s,%s)
        """,
        (username, email, hashed_password)
    )

    mysql.connection.commit()
    cur.close()

    return True, "Registration successful"


def login_user(email, password):

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT id, username, email, password
        FROM users
        WHERE email=%s
        """,
        (email,)
    )

    user = cur.fetchone()

    if not user:
        return False, "Email not found", None

    stored_password = user[3]

    if check_password_hash(stored_password, password):
        return True, "Login successful", user

    return False, "Invalid password", None

