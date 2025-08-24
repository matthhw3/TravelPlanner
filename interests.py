from flask import Blueprint, session, render_template, request, redirect
import json
from models import UserInterests, db


interests_bp = Blueprint("interests", __name__)

@interests_bp.route("/interests", methods=["GET", "POST"])
def interests():
    user_id = session["user_id"]

    with open("keywords.json") as f:
        keyword_map = json.load(f)

    interests_list = []
    for key in keyword_map.keys():
        interests_list.append(key)

    if request.method == "POST":
        selected_interests = set(request.form.getlist("interests"))

        current_interests = set(i.interest for i in UserInterests.query.filter_by(user_id=user_id).all())

        to_add = selected_interests - current_interests
        to_remove = current_interests - selected_interests

        for interest in to_add:
            db.session.add(UserInterests(user_id=user_id, interest=interest))
        
        for interest in to_remove:
            UserInterests.query.filter_by(user_id=user_id, interest=interest).delete()

        db.session.commit()
        return redirect("/interests")
    
    saved_interests = set(i.interest for i in UserInterests.query.filter_by(user_id=user_id).all())
    
    return render_template("match.html", interests_list = interests_list, saved_interests = saved_interests, initials=session.get("initials"))
