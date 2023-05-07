import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, time as dt_time, timedelta


from helpers import apology, login_required, usd, weather

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///weather.db")

# Make sure API key is set
if not os.environ["API_KEY"]:
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Show weather in icon form"""
    place = db.execute('SELECT place FROM users WHERE id = ?', session.get('user_id'))
    city = place[0]["place"]
    wet = weather(city)
    data = wet[0]
    forecast = wet[1]
    if wet == None:
        return apology("PLEASE CHECK YOU INTERNET COONECTION", 404)
    return render_template("home.html", wet=data, forecast=forecast)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/ask", methods=["GET", "POST"])
@login_required
def ask():
    """Get weather of a place"""
    if request.method == 'POST':
        place = request.form.get('place')
        if not place:
            return apology("ENTER VALID PLACE", 400)
        wet = weather(place)
        if wet == None:
            return apology('INVALID PLACE', 400)
        data = wet[0]
        return render_template('weather.html', wet=data)
    return render_template('ask.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        place = request.form.get("city")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        wet = weather(place)
        if not username:
            return apology('INVALID USERNAME', 400)
        elif not password:
            return apology('ENTER PASSWORD', 400)
        elif not place:
            return apology('ENTER PLACE', 400)
        elif not password == confirmation:
            return apology('INVALID PASSWORD', 400)
        elif wet == None:
            return apology('SORRY! PLEASE GIVE ANOTHER PLACE', 400)
        else:
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
            if len(rows) == 1:
                return apology('USER ALREADY EXITS', 400)
            else:
                hash = generate_password_hash(password)
                db.execute('INSERT INTO users(username, hash, place) VALUES (?, ?, ?)', username, hash, place)
                return redirect("/")
    return render_template('register.html')


@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    """Stores the feedback of the users"""
    if request.method == "POST":
        feedback = request.form.get("feedback")
        db.execute('INSERT INTO feedback(feedback) VALUES (?)', feedback)
    rows = db.execute('SELECT * FROM feedback')
    return render_template("feedback.html", rows=rows)


@app.route("/subscribe", methods=["GET", "POST"])
@login_required
def subscribe():
    """Saves the name of all subscribers into the database"""
    if request.method == 'POST':
        place = request.form.get("place")
        mail = request.form.get("mail")
        if not place:
            return apology("ENTER VALID PLACE", 400)
        if not mail:
            return apology("ENTER YOUR MAIL ID", 400)
        wet = weather(place)
        if wet == None:
            return apology('INVALID PLACE', 400)
        username = db.execute('SELECT username FROM users WHERE id = ?', session["user_id"])
        db.execute('INSERT INTO subscribers(username, place, email) VALUES (?,?,?)', username[0]["username"],place, mail)
        flash('You have successfully subscribed for daily mails!', 'success')
    return render_template("subscribe.html")
    



