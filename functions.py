import os, math, ssl, requests, polyline
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GRAPHOPPER_KEY")
if not KEY:
    raise RuntimeError("GRAPHOPPER_KEY missing")

_secure = Nominatim(user_agent="quakesafe", timeout=5)
_insecure_ctx = ssl.create_default_context()
_insecure_ctx.check_hostname = False
_insecure_ctx.verify_mode = ssl.CERT_NONE
_insecure = Nominatim(user_agent="quakesafe", timeout=5, ssl_context=_insecure_ctx)

def geocode(addr: str):
    try:
        loc = _secure.geocode(addr)
    except ssl.SSLError:
        loc = _insecure.geocode(addr)
    return (loc.latitude, loc.longitude) if loc else None

USGS = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
def latest_eq(min_mag=3.0):
    feats = requests.get(USGS, timeout=6).json()["features"]
    for f in feats:
        if f["properties"]["mag"] and f["properties"]["mag"] >= min_mag:
            lon, lat, *_ = f["geometry"]["coordinates"]
            return f["properties"]["mag"], (lat, lon)
    return None

def haversine(p1, p2):
    R = 6371
    lat1, lon1 = map(math.radians, p1)
    lat2, lon2 = map(math.radians, p2)
    dlat, dlon = lat2-lat1, lon2-lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 2*R*math.asin(math.sqrt(a))

def route_safe(coords, quake, radius=20):
    if not quake:
        return True
    _, eq = quake
    return all(haversine(pt, eq) >= radius for pt in coords)

GH = "https://graphhopper.com/api/1/route"
def get_route(orig, dest):
    params = {
        "key": KEY,
        "vehicle": "car",
        "point": [f"{orig[0]},{orig[1]}", f"{dest[0]},{dest[1]}"],
        "points_encoded": "false",
    }
    r = requests.get(GH, params=params, timeout=10)
    r.raise_for_status()
    path = r.json()["paths"][0]
    coords = [(p[1], p[0]) for p in path["points"]["coordinates"]]
    return {
        "coords": coords,
        "distance_km": round(path["distance"]/1000, 2),
        "time_min": round(path["time"]/60000, 1),
    }




