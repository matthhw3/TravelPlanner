from flask import Blueprint, request, redirect, render_template, session, url_for, flash
from models import db, User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()

        if existing_user and existing_user.password == password:
            session["first_name"] = existing_user.first_name
            session["last_name"] = existing_user.last_name
            session["initials"] = (existing_user.first_name[0] + existing_user.last_name[0]).upper()
            session["user_id"] = existing_user.id
            return redirect(url_for("trips.dashboard"))

        flash("Invalid Username or Password")
        return redirect("/")
    
@auth_bp.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("go_create"))

        new_user = User(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(new_user)
        db.session.commit()

        session["first_name"] = first_name
        session["last_name"] = last_name
        session["initials"] = (first_name[0] + last_name[0]).upper()
        session["user_id"] = new_user.id

        return redirect(url_for("trips.dashboard"))

    return redirect(url_for("trips.dashboard"))
