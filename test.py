import requests

api_key = "IDSZ2RGNR22VIMD5VZEFPOKD01Y40G1ZUE3PC3EN0G1TH1CE"
url = "https://api.foursquare.com/v3/places/search"
params = {
    "ll": "37.7749,-122.4194",
    "radius": "1000",
    "limit": "5"
}
headers = {
    "Accept": "application/json",
    "Authorization": api_key
}

response = requests.get(url, headers=headers, params=params)
print("Status:", response.status_code)
print("Response:", response.text)