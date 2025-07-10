from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import json


app = Flask(__name__)
app.secret_key = "apple"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travelplanner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure = db.Column(db.String(20), nullable=False)
    return_date = db.Column(db.String(20), nullable=False)
    travelers = db.Column(db.String(200), nullable=False)
    flight = db.Column(db.String(50))
    boarding_time = db.Column(db.String(20))
    image = db.Column(db.String(500))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)

@app.route("/dashboard")
def dashboard():
    trips = load_trips()
    initials = session.get("initials")
    return render_template("dashboard.html", trips = trips, initials = initials)

@app.route("/plan")
def plan():
    return render_template("plan.html")

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            if existing_user.password == password:
                session["first_name"] = existing_user.first_name
                session["last_name"] = existing_user.last_name
                session["initials"] = "".join([existing_user.first_name[0], existing_user.last_name[0]]).upper()
                trips = load_trips()
                return redirect(url_for("dashboard", username=username))

            flash("Invalid Username or Password")
        return render_template("login.html")

@app.route("/go_create", methods=["GET", "POST"])
def go_create():
    return render_template("create.html")

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists")
            return render_template("create.html")

        # Create new user record
        new_user = User(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully")
        return render_template("dashboard.html")

    redirect("/dashboard")


def load_trips():
    return Trip.query.all()

def load_valid_destinations():
    with open("places.json") as file:
        valid = []
        data = json.load(file)
        for entry in data:
            valid.append(entry["destination"].strip().lower())
        return valid

def get_image(destination):
    with open('places.json') as f:
        data = json.load(f)
    for entry in data:
        if entry["destination"].lower() == destination.lower():
            return entry["image"]
    return None

@app.route("/create_trip", methods=["POST"])
def create_trip():

    destination = request.form["destination"]
    destination_clean = destination.strip().lower()

    valid_destinations = load_valid_destinations()
    if destination_clean not in valid_destinations:
        flash(f'Sorry, {destination} is not currently supported.')
        return render_template("plan.html")

    trip_name = request.form["trip_name"]
    origin = request.form["origin"]
    departure = request.form["departure"]
    return_date = request.form["return"]
    travelers = request.form["travelers"]

    new_trip = Trip(
        trip_name=trip_name,
        origin=origin,
        destination=destination,
        departure=departure,
        return_date=return_date,
        travelers=travelers,
        image=get_image(destination)
    )

    db.session.add(new_trip)
    db.session.commit()

    flash("Trip created successfully")
    return redirect("/dashboard")

@app.route("/delete_trip", methods=["POST"])
def delete_trip():
    trip_id = request.form["trip_id"]
    trip = Trip.query.get_or_404(trip_id)
    db.session.delete(trip)
    db.session.commit()
    flash("Trip deleted successfully")
    return redirect("/dashboard")
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
