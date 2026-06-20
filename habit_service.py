from flask_mysqldb import MySQL
from db import mysql
from datetime import date, timedelta
def add_habit(user_id, habit_name, description, frequency):

    cur = mysql.connection.cursor()

    cur.execute(
        """
        INSERT INTO habits
        (user_id, habit_name, description, frequency)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, habit_name, description, frequency)
    )

    mysql.connection.commit()

    return True, "Habit added successfully"


def get_habits_by_user(user_id):

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT id,
               habit_name,
               description,
               frequency
        FROM habits
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    habits = cur.fetchall()

    return habits

def get_habit_by_id(habit_id, user_id):

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT id,
               habit_name,
               description,
               frequency
        FROM habits
        WHERE id=%s
        AND user_id=%s
        """,
        (habit_id, user_id)
    )

    return cur.fetchone()


def update_habit(
        habit_id,
        user_id,
        habit_name,
        description,
        frequency):

    cur = mysql.connection.cursor()

    cur.execute(
        """
        UPDATE habits
        SET habit_name=%s,
            description=%s,
            frequency=%s
        WHERE id=%s
        AND user_id=%s
        """,
        (
            habit_name,
            description,
            frequency,
            habit_id,
            user_id
        )
    )

    mysql.connection.commit()

    if cur.rowcount == 0:
        return False, "Habit not found"

    return True, "Habit updated successfully"


def delete_habit(habit_id, user_id):

    cur = mysql.connection.cursor()

    cur.execute(
        """
        DELETE FROM habits
        WHERE id=%s
        AND user_id=%s
        """,
        (habit_id, user_id)
    )

    mysql.connection.commit()

    if cur.rowcount == 0:
        return False, "Habit not found"

    return True, "Habit deleted successfully"

def mark_habit_complete(habit_id):

    today = date.today()

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM habit_logs
        WHERE habit_id=%s
        AND completed_date=%s
        """,
        (habit_id, today)
    )

    already_completed = cur.fetchone()

    if already_completed:
        return False, "Habit already completed today"

    cur.execute(
        """
        INSERT INTO habit_logs
        (habit_id, completed_date)
        VALUES(%s, %s)
        """,
        (habit_id, today)
    )

    mysql.connection.commit()

    return True, "Habit completed"

def get_completion_dates(habit_id):

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT completed_date
        FROM habit_logs
        WHERE habit_id=%s
        ORDER BY completed_date
        """,
        (habit_id,)
    )

    rows = cur.fetchall()

    return [row[0] for row in rows]

def calculate_current_streak(habit_id):

    dates = get_completion_dates(habit_id)

    if not dates:
        return 0

    dates = set(dates)

    streak = 0
    current_day = date.today()

    while current_day in dates:

        streak += 1

        current_day -= timedelta(days=1)

    return streak

def calculate_longest_streak(habit_id):

    dates = get_completion_dates(habit_id)

    if not dates:
        return 0


    longest = 1
    current = 1

    for i in range(1, len(dates)):

        difference = (
            dates[i] - dates[i-1]
        ).days

        if difference == 1:

            current += 1

            longest = max(
                longest,
                current
            )

        else:

            current = 1

    return longest