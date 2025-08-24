from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify
import os
from models import db, Activity, Trip, TripMember
from dotenv import load_dotenv
from utils.helpers import get_cords, search_nearby_places, get_keywords, get_place_details
from random import shuffle

load_dotenv()
GOOGLECLOUD_API = os.getenv("GOOGLECLOUDAPI")

explore_bp = Blueprint("explore", __name__)

def _wants_json():
    return request.form.get("ajax") == "1" or \
           request.headers.get("X-Requested-With") == "XMLHttpRequest" or \
           "application/json" in (request.headers.get("Accept") or "")

@explore_bp.route("/nearby", methods=["GET", "POST"])
def nearby():
    google_api_key = GOOGLECLOUD_API
    user_id = session.get("user_id")

    trips = []
    if user_id:
        owned = Trip.query.filter_by(user_id=user_id).all()
        invited = db.session.query(Trip).join(TripMember)\
                   .filter(TripMember.member_user_id == user_id, Trip.user_id != user_id).all()
        trips = owned + invited

    if request.method == "POST":
        action = request.form.get("action")
        location = request.form.get("location")
        mode = request.form.get("mode")
        radius = 1500 if mode == "walk" else 15000

        lat, lon = get_cords(location)

        if action == "randomize":
            user_id = session.get("user_id")
            random_keywords = get_keywords(user_id, num_keywords=3)
            places, seen = [], set()
            for kw in random_keywords:
                results = search_nearby_places(lat, lon, radius=radius, keyword=kw)
                cnt = 0
                for place in results:
                    pid = place.get("place_id")
                    if pid and pid not in seen:
                        places.append(place); seen.add(pid); cnt += 1
                    if cnt >= 5: break
            from random import shuffle; shuffle(places)
        else:
            places = search_nearby_places(lat, lon, radius=radius)

        return render_template(
            "nearby.html",
            places=places, location=location, lat=lat, lon=lon,
            initials=session.get("initials"),
            google_api_key=google_api_key,
            trips=trips,
        )

    return render_template(
        "nearby.html",
        places=None,
        initials=session.get("initials"),
        google_api_key=google_api_key,
        trips=trips,
    )

@explore_bp.route("/nearby/add", methods=["POST"])
def add_nearby_to_trip():
    is_ajax = _wants_json()
    if not session.get("user_id"):
        return (jsonify({"ok": False, "error": "Please sign in."}), 401) if is_ajax else redirect(url_for("home"))

    place_id = request.form.get("place_id")
    trip_id = request.form.get("trip_id", type=int)
    if not place_id or not trip_id:
        return (jsonify({"ok": False, "error": "Select a trip."}), 400) if is_ajax else redirect(url_for("explore.nearby"))

    d = get_place_details(place_id) or {}
    photo_ref = (d.get("photos") or [{}])[0].get("photo_reference")
    summary = (d.get("editorial_summary") or {}).get("overview")
    estimate = {0:0, 1:15, 2:30, 3:55, 4:90}.get(d.get("price_level") or 0, 0)

    a = Activity(
        trip_id=trip_id, status="staged", source="google_places",
        place_id=place_id, name=d.get("name") or "Untitled",
        short_desc=summary, image_ref=photo_ref, category="activity",
        pricing_type="per_person", unit_price=float(estimate),
        qty=1, tax_pct=0.0, fees=0.0,
    )
    db.session.add(a); db.session.commit()

    return (jsonify({"ok": True, "activity": {"id": a.id, "name": a.name}}), 201) if is_ajax \
           else redirect(url_for("trips.trip_details", trip_id=trip_id))