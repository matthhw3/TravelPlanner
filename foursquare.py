import requests

FOURSQUARE_API_KEY = "IDSZ2RGNR22VIMD5VZEFPOKD01Y40G1ZUE3PC3EN0G1TH1CE"


def search_nearby_places(lat, lon, query="restaurant", radius=1000, limit=8):
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "Authorization": FOURSQUARE_API_KEY
    }
    params = {
        "ll": f"{lat},{lon}",
        "query": query,
        "radius": radius,
        "limit": limit
    }

    response = requests.get(url, headers=headers, params=params)
    results = response.json().get("results", [])

    return results
