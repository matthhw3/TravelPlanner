from flask import Flask, render_template, request, redirect, url_for, flash
import json

app = Flask(__name__)
app.secret_key = "apple"

@app.route("/dashboard")
def dashboard():
    return "<h1>Welcome to your Travel Planner Dashboard!</h1>"

def load_users():
    with open("users.json", "r") as file:
        return json.load(file)

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            if password == users[username]["password"]:
                flash("Login Successful")
                return render_template("dashboard.html")
        else:
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

        with open("users.json", "r") as file:
            user_list = json.load(file)

        if username in user_list:
            flash("Username already exists")
            return render_template("create.html")

        user_list[username] = {"password": password}

        with open("users.json", "w") as file:
            json.dump(user_list, file)

        flash("Account created successfully")
        return render_template("dashboard.html")
        

if __name__ == "__main__":
    app.run(debug=True)
