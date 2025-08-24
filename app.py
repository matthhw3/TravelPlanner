from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Trip
from auth import auth_bp
from trips import trips_bp
from explore_routes import explore_bp
from interests import interests_bp
import os
from dotenv import load_dotenv
from pathlib import Path

app = Flask(__name__)
app.secret_key = "apple"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH  = BASE_DIR / "travelplanner.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH.as_posix()}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

load_dotenv()
app.config['GOOGLE_API_KEY'] = os.getenv('GOOGLECLOUDAPI')

db.init_app(app)

@app.context_processor
def inject_google_key():
    return {"google_api_key": app.config.get("GOOGLE_API_KEY", "")}

app.register_blueprint(auth_bp)
app.register_blueprint(trips_bp)
app.register_blueprint(explore_bp)
app.register_blueprint(interests_bp)

@app.get("/__dbinfo")
def __dbinfo():
    return {
        "db_uri": app.config["SQLALCHEMY_DATABASE_URI"],
        "db_file": db.engine.url.database,
        "exists": Path(db.engine.url.database).exists()
    }

@app.route("/plan")
def plan():
    return render_template("plan.html", initials=session.get("initials"))


@app.route("/trip/<int:trip_id>")
def trip_details(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    return render_template("trip_details.html", trip=trip, initials=session.get("initials"))

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("login.html")

@app.route("/go_create", methods=["GET", "POST"])
def go_create():
    return render_template("create_account.html")

if __name__ == "__main__":
    with app.app_context():
        print("USING DB:", db.engine.url.database, "exists:", Path(db.engine.url.database).exists())
        """db.create_all()"""
    app.run(debug=True)