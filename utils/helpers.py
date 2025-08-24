import json
import os
import requests
from dotenv import load_dotenv
import random
from models import UserInterests

load_dotenv()
GOOGLECLOUD_API = os.getenv("GOOGLECLOUDAPI")

def get_image(destination):
    with open('places.json') as f:
        data = json.load(f)
    for entry in data:
        if entry["destination"] == destination:
            return entry["image"]
    return None

def get_cords(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address":address, "key":GOOGLECLOUD_API}
    
    response = requests.get(url, params=params)

    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            location = results[0]["geometry"]["location"]
            return location["lat"], location["lng"]
    return None, None

def search_nearby_places(lat, lon, radius=1000, keyword="restaurant"):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "key": GOOGLECLOUD_API,
        "location": f"{lat},{lon}",
        "radius": radius,
        "keyword": keyword
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json().get("results", [])
    return []

def get_keywords(user_id, keyword_file='keywords.json', num_keywords=3):
    with open(keyword_file) as f:
        keyword_map = json.load(f)

    user_interests = [i.interest for i in UserInterests.query.filter_by(user_id=user_id).all()]

    all_keywords = []

    for interest in user_interests:
        if interest in keyword_map:
            for sub_keywords in keyword_map[interest].values():
                all_keywords.extend(sub_keywords)

    if not all_keywords:
        return ["restaurant"]

    return random.sample(all_keywords, min(num_keywords, len(all_keywords)))

def get_place_details(place_id):
    fields = ",".join([
        "name","editorial_summary","rating","user_ratings_total",
        "price_level","photos","reviews","formatted_address","url", "types", "opening_hours"
    ])
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={GOOGLECLOUD_API}"
    return requests.get(url, timeout=10).json().get("result", {})

def find_place_by_text(query):
    """Return the best Google place for a free-text query."""
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "key": GOOGLECLOUD_API,
        "input": query,
        "inputtype": "textquery",
        "fields": "place_id,name,formatted_address,types,photos"
    }
    r = requests.get(url, params=params, timeout=10).json()
    cands = r.get("candidates") or []
    if not cands:
        return None
    best = cands[0]
    photo_ref = None
    if best.get("photos"):
        photo_ref = best["photos"][0].get("photo_reference")
    return {
        "place_id": best.get("place_id"),
        "name": best.get("name"),
        "address": best.get("formatted_address"),
        "types": best.get("types") or [],
        "photo_ref": photo_ref
    }