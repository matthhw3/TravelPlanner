from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_name = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure = db.Column(db.String(20), nullable=False)
    return_date = db.Column(db.String(20), nullable=False)
    travelers = db.Column(db.String(200), nullable=False)
    flight = db.Column(db.String(50))
    image = db.Column(db.String(500))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class TripMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    member_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship("User", backref="trip_memberships")
    trip = db.relationship("Trip", backref="members")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)

class UserInterests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    interest = db.Column(db.String(50), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'interest', name='unique_user_interest'),)

class Budget(db.Model):
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), primary_key=True)
    amount_total = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(8), default="USD")

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)

class Activity(db.Model):
    __tablename__ = "activity"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)

    status = db.Column(db.String(32), default="staged", nullable=False)
    source = db.Column(db.String(32))

    place_id = db.Column(db.String(128))
    name = db.Column(db.String(200), nullable=False)
    short_desc = db.Column(db.Text)
    image_ref = db.Column(db.String(300))

    category = db.Column(db.String(64), default="activity")
    pricing_type = db.Column(db.String(32), default="per_person")
    unit_price = db.Column(db.Float, default=0.0)
    qty = db.Column(db.Integer, default=1)
    tax_pct = db.Column(db.Float, default=0.0)
    fees = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (db.UniqueConstraint('trip_id', 'place_id', name='uniq_trip_place'),)

class ItineraryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)

class Vote(db.Model):
    __tablename__ = "vote"
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stars = db.Column('value', db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint('trip_id','activity_id','user_id', name='uniq_vote'),)
