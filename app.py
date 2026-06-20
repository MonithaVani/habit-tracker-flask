from flask import Flask, render_template, request, redirect, url_for, flash, session
from user_service import register_user, login_user
from habit_service import (
    add_habit,
    get_habits_by_user,
    get_habit_by_id,
    update_habit,
    delete_habit,
    mark_habit_complete, calculate_current_streak, calculate_longest_streak
)
import config
from db import mysql

app = Flask(__name__)

app.secret_key = "habit_tracker_secret"

# MySQL Config
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql.init_app(app)


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        success, message = register_user(
            username,
            email,
            password
        )

        flash(message)

        if success:
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        success, message, user = login_user(
            email,
            password
        )

        if success:

            session['user_id'] = user[0]
            session['username'] = user[1]

            flash(message)

            return redirect(url_for('dashboard'))

        flash(message)

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    habits = get_habits_by_user(
        session['user_id']
    )

    habit_data = []

    for habit in habits:
        current_streak = calculate_current_streak(
            habit[0]
        )

        longest_streak = calculate_longest_streak(
            habit[0]
        )

        habit_data.append({

            "id": habit[0],
            "name": habit[1],
            "description": habit[2],
            "frequency": habit[3],

            "current_streak": current_streak,
            "longest_streak": longest_streak

        })
    return render_template(
        "dashboard.html",
        username=session['username'],
        habits=habit_data
    )

@app.route('/logout')
def logout():

    session.clear()

    flash("Logged out successfully")

    return redirect(url_for('login'))

@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit_page():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        habit_name = request.form['habit_name']
        description = request.form['description']
        frequency = request.form['frequency']

        success, message = add_habit(
            session['user_id'],
            habit_name,
            description,
            frequency
        )

        flash(message)

        return redirect(url_for('dashboard'))

    return render_template('add_habit.html')

@app.route('/edit_habit/<int:habit_id>',
           methods=['GET', 'POST'])
def edit_habit_page(habit_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        habit_name = request.form['habit_name']
        description = request.form['description']
        frequency = request.form['frequency']

        success, message = update_habit(
            habit_id,
            session['user_id'],
            habit_name,
            description,
            frequency
        )

        flash(message)

        return redirect(url_for('dashboard'))

    habit = get_habit_by_id(
        habit_id,
        session['user_id']
    )
    if not habit:
        flash("Unauthorized access")
        return redirect(url_for('dashboard'))

    return render_template(
        'edit_habit.html',
        habit=habit
    )

@app.route('/delete_habit/<int:habit_id>')
def delete_habit_page(habit_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    success, message = delete_habit(
        habit_id,
        session['user_id']
    )
    flash(message)

    return redirect(url_for('dashboard'))

@app.route('/complete_habit/<int:habit_id>')
def complete_habit(habit_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    success, message = mark_habit_complete(habit_id)

    flash(message)

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)