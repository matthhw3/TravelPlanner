from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import date as _date, datetime, timedelta
from models import db, Trip, Activity, TripMember, User
from utils.helpers import get_place_details, GOOGLECLOUD_API, get_image, find_place_by_text

trips_bp = Blueprint("trips", __name__)

@trips_bp.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/")

    trips = Trip.query.filter_by(user_id=user_id).all()
    invited_trips = db.session.query(Trip).join(TripMember).filter(TripMember.member_user_id == user_id, Trip.user_id != user_id).all()

    all_trips = trips + invited_trips
    return render_template("dashboard.html", trips = all_trips, initials = session.get("initials"))

@trips_bp.route("/create_trip", methods=["POST"])
def create_trip():
    user_id = session.get("user_id")
    destination = request.form["destination"]
    trip_name = request.form["trip_name"]
    origin = request.form["origin"]
    departure = request.form["departure"]
    return_date = request.form["return"]

    invited_users = request.form.get("invited_users", "")

    new_trip = Trip(
        trip_name=trip_name,
        origin=origin,
        destination=destination,
        departure=departure,
        return_date=return_date,
        travelers="",
        image=get_image(destination),
        user_id=user_id
    )

    db.session.add(new_trip)
    db.session.commit()

    usernames = [u.strip() for u in invited_users.split(",") if u.strip().lower()!="none"]
    failed_invites = []

    for username in usernames:
        user = User.query.filter_by(username=username).first()
        if user:
            if user.id != user_id:
                already_invited = TripMember.query.filter_by(trip_id=new_trip.id, member_user_id=user.id).first()
                if not already_invited:
                    db.session.add(TripMember(trip_id=new_trip.id, member_user_id=user.id))
        else:
            failed_invites.append(username)
    
    db.session.commit()

    member_names = db.session.query(User.first_name, User.last_name).join(TripMember).filter(TripMember.trip_id == new_trip.id).all()
    
    all_members = member_names
    all_members.insert(0, db.session.query(User.first_name, User.last_name).filter(User.id == new_trip.user_id).first())

    new_trip.travelers = ", ".join([f"{first} {last}" for first, last in all_members])
    db.session.commit()

    return redirect(url_for("trips.dashboard"))

@trips_bp.route("/delete_trip", methods=["POST"])
def delete_trip():
    trip_id = request.form.get("trip_id")

    trip = Trip.query.get_or_404(trip_id)

    db.session.delete(trip)
    db.session.commit()
    return redirect(url_for("trips.dashboard"))

@trips_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

from models import Assignment
try:
    from models import Vote
except Exception:
    Vote = None

def _as_date(val):
    if isinstance(val, _date): return val
    if isinstance(val, str):
        s = val.strip()
        try: return _date.fromisoformat(s[:10])
        except: pass
        try: return datetime.strptime(s[:10], "%Y-%m-%d").date()
        except: pass
    if hasattr(val, "date"): return val.date()
    raise ValueError(f"Cannot parse date from {val!r}")

def _trip_days(trip):
    start = _as_date(trip.departure)
    end   = _as_date(trip.return_date)
    days = []
    d = start
    while d <= end:
        days.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)
    return days

def group_match_percent(trip_id, scheduled_by_day):
    if not Vote: return None
    scores, seen = [], set()
    for acts in scheduled_by_day.values():
        for a in acts:
            aid = a["id"]
            if aid in seen: continue
            seen.add(aid)
            vs = Vote.query.filter_by(activity_id=aid).all()
            if not vs: continue
            avg = sum(v.stars for v in vs) / len(vs)
            scores.append((avg/5.0)*100.0)
    return sum(scores)/len(scores) if scores else None

_TOP_CATS = {
    "food": {"restaurant","cafe","bakery","bar","meal_takeaway","meal_delivery"},
    "culture": {"museum","art_gallery","library","place_of_worship"},
    "shopping": {"shopping_mall","store","clothing_store","department_store","jewelry_store"},
    "nature": {"park","campground","zoo","aquarium","botanical_garden"},
    "nightlife": {"bar","night_club"},
    "entertainment": {"tourist_attraction","amusement_park","movie_theater"},
    "wellness": {"spa","gym","beauty_salon"},
}
def infer_category_for_activity(a):
    if getattr(a, "category", None) and a.category != "activity":
        return a.category
    if a.place_id:
        d = get_place_details(a.place_id) or {}
        types = set(d.get("types") or [])
        for top, kids in _TOP_CATS.items():
            if types & kids:
                return top
    return "other"

def diversity_from(by_day):
    counts = {}
    for acts in by_day.values():
        for a in acts:
            cat = a.get("category") or "other"
            counts[cat] = counts.get(cat, 0) + 1
    if not counts:
        return {"labels": [], "values": []}
    labels = list(counts.keys())
    values = [counts[k] for k in labels]
    return {"labels": labels, "values": values}

def needs_reservation(place_details):
    if not place_details: return False
    types = set(place_details.get("types") or [])
    rating = place_details.get("rating") or 0
    total  = place_details.get("user_ratings_total") or 0
    summary = ((place_details.get("editorial_summary") or {}).get("overview") or "").lower()
    name = (place_details.get("name") or "").lower()

    if any(k in summary for k in ["reservation", "book", "tickets required", "advance tickets"]):
        return True

    if types & {"restaurant","bar","cafe","bakery"}:
        if rating >= 4.3 and total >= 150:
            return True

    if types & {"tourist_attraction","museum","art_gallery","aquarium","zoo","amusement_park"}:
        if total >= 500:
            return True

    if any(k in name for k in ["omakase","tasting menu","michelin"]):
        return True

    return False

def _state(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    days = _trip_days(trip)
    by_day = {d: [] for d in days}

    assigned_ids = [r.activity_id for r in Assignment.query.filter_by(trip_id=trip_id).all()]
    q = Activity.query.filter_by(trip_id=trip_id)
    if assigned_ids:
        q = q.filter(~Activity.id.in_(assigned_ids))
    staged = q.order_by(Activity.created_at.desc()).all()

    rows = db.session.query(Assignment, Activity)\
            .join(Activity, Assignment.activity_id == Activity.id)\
            .filter(Assignment.trip_id == trip_id).all()
    for asg, act in rows:
        by_day.setdefault(asg.day, []).append({
            "id": act.id,
            "name": act.name,
            "image_ref": act.image_ref,
            "category": infer_category_for_activity(act)
        })

    return trip, staged, by_day, days

@trips_bp.route("/trip/<int:trip_id>")
def trip_details(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    return render_template("trip_details.html", trip=trip, google_api_key=GOOGLECLOUD_API, initials=session.get("initials"))

@trips_bp.get("/api/trips/<int:trip_id>/staged")
def api_trip_staged(trip_id):
    acts = Activity.query.filter_by(trip_id=trip_id, status="staged")\
                         .order_by(Activity.created_at.desc()).all()
    return jsonify([{
        "id": a.id, "name": a.name,
        "image_ref": a.image_ref, "place_id": a.place_id
    } for a in acts])

@trips_bp.get("/api/trips/<int:trip_id>/state")
def api_trip_state(trip_id):
    trip, staged, by_day, days = _state(trip_id)
    gm = group_match_percent(trip_id, by_day)
    diversity = diversity_from(by_day)
    return jsonify({
        "days": days,
        "scheduled_by_day": by_day,
        "diversity": diversity,
        "group_match_percent": gm
    })

@trips_bp.get("/api/trips/<int:trip_id>/reservations")
def api_trip_reservations(trip_id):
    _, _, by_day, _ = _state(trip_id)
    results, seen = [], set()
    for acts in by_day.values():
        for a in acts:
            if a["id"] in seen: continue
            seen.add(a["id"])
            act = Activity.query.get(a["id"])
            d = get_place_details(act.place_id) if act.place_id else {}
            if needs_reservation(d):
                results.append({
                    "id": act.id, "name": act.name, "image_ref": act.image_ref
                })
    return jsonify(results)

@trips_bp.post("/trips/<int:trip_id>/schedule")
def api_schedule(trip_id):
    data = request.get_json() or {}
    a_id = int(data.get("activity_id"))
    day = data.get("date")

    Assignment.query.filter_by(trip_id=trip_id, activity_id=a_id).delete()

    act = Activity.query.get_or_404(a_id)
    act.status = "planned"

    db.session.add(Assignment(trip_id=trip_id, activity_id=a_id, day=day))
    db.session.commit()
    return jsonify({"ok": True})


@trips_bp.post("/trips/<int:trip_id>/unschedule")
def api_unschedule(trip_id):
    data = request.get_json() or {}
    a_id = int(data.get("activity_id"))

    Assignment.query.filter_by(trip_id=trip_id, activity_id=a_id).delete()

    act = Activity.query.get(a_id)
    if act:
        act.status = "staged"

    db.session.commit()
    return jsonify({"ok": True})

@trips_bp.post("/trips/<int:trip_id>/activities/manual")
def add_manual_activity(trip_id):
    title = (request.form.get("title") or "").strip()
    location = (request.form.get("location") or "").strip()
    if not title or not location:
        return jsonify({"ok": False, "error": "Title and location required."}), 400

    picked = find_place_by_text(f"{title} {location}") or find_place_by_text(location)
    place_id = image_ref = short_desc = None
    category = "activity"

    if picked and picked.get("place_id"):
        place_id = picked["place_id"]
        image_ref = picked.get("photo_ref")
        d = get_place_details(place_id) or {}
        short_desc = (d.get("editorial_summary") or {}).get("overview")

    a = Activity(
        trip_id=trip_id, status="staged", source="manual",
        place_id=place_id, name=title, short_desc=short_desc,
        image_ref=image_ref, category=category
    )
    db.session.add(a); db.session.commit()
    return jsonify({"ok": True, "id": a.id})

@trips_bp.post("/trips/<int:trip_id>/activities/<int:activity_id>/delete")
def ui_delete_activity(trip_id, activity_id):
    a = Activity.query.filter_by(id=activity_id, trip_id=trip_id).first_or_404()
    if a.status != "staged":
        return jsonify({"ok": False, "error": "Unschedule first"}), 409
    db.session.delete(a)
    db.session.commit()
    return jsonify({"ok": True})

@trips_bp.get("/api/activities/<int:activity_id>/details")
def api_activity_details(activity_id):
    a = Activity.query.get_or_404(activity_id)
    d = {}
    try:
        if a.place_id:
            d = get_place_details(a.place_id) or {}
    except Exception:
        d = {}
    uid = session.get("user_id")
    my_stars = None
    try:
        if uid:
            v = Vote.query.filter_by(trip_id=a.trip_id, activity_id=a.id, user_id=uid).first()
            if v: my_stars = v.stars
    except Exception:
        pass
    return jsonify({
        "id": a.id,
        "name": d.get("name") or a.name,
        "summary": (d.get("editorial_summary") or {}).get("overview") or (a.short_desc or ""),
        "rating": d.get("rating"),
        "ratings_total": d.get("user_ratings_total"),
        "photo_refs": [p.get("photo_reference") for p in (d.get("photos") or [])[:6]],
        "reviews": [
            {"author": r.get("author_name") or "Reviewer",
             "text": r.get("text"), "stars": r.get("rating")}
            for r in (d.get("reviews") or [])[:4] if r.get("text")
        ],
        "my_stars": my_stars
    })

@trips_bp.post("/api/activities/<int:activity_id>/vote")
def api_activity_vote(activity_id):
    if not Vote:
        return jsonify({"ok": False, "error": "Voting model not available"}), 500

    uid = session.get("user_id")
    if not uid:
        return jsonify({"ok": False, "error": "Sign in required"}), 401

    data = request.get_json() or {}
    stars = int(data.get("stars", 0))
    if stars < 1 or stars > 5:
        return jsonify({"ok": False, "error": "Stars must be 1–5"}), 400

    a = Activity.query.get_or_404(activity_id)
    trip_id = a.trip_id

    v = Vote.query.filter_by(trip_id=trip_id, activity_id=activity_id, user_id=uid).first()
    if not v:
        v = Vote(trip_id=trip_id, activity_id=activity_id, user_id=uid, stars=stars)
        db.session.add(v)
    else:
        v.stars = stars

    db.session.commit()
    return jsonify({"ok": True})

