import io
import csv
from unidecode import unidecode
from django.contrib.gis.geos import Point, Polygon

def sanitize_label(label):
    """
    Converts a string to ASCII (Latinized) and replaces spaces with underscores.
    Example: "Warszawa Śródmieście" -> "Warszawa_Srodmiescie"
    """
    if not label:
        return ""
    return unidecode(label).replace(" ", "_")

def parse_polygon_coords(coord_string):
    """
    Parses a coordinate string "lat lon,lat lon,lat lon,..." into a list of (lat, lon) tuples.
    """
    coords = []
    for pair in coord_string.split(","):
        try:
            lat_str, lon_str = pair.strip().split()
            coords.append((float(lat_str), float(lon_str)))
        except ValueError:
            continue
    return coords

def compute_bounds(coords):
    """
    Given a list of (lat, lon) tuples, computes (min_lon, min_lat, max_lon, max_lat).
    """
    if not coords:
        return None
    min_lat = min(lat for lat, lon in coords)
    max_lat = max(lat for lat, lon in coords)
    min_lon = min(lon for lat, lon in coords)
    max_lon = max(lon for lat, lon in coords)
    return min_lon, min_lat, max_lon, max_lat

def is_polygon_too_large(coords, threshold=0.5):
    """
    Checks if the bounding box of the polygon (given as (lat, lon) tuples)
    exceeds the threshold (in degrees) in width or height.
    """
    bounds = compute_bounds(coords)
    if not bounds:
        return False
    min_lon, min_lat, max_lon, max_lat = bounds
    return (max_lon - min_lon) > threshold or (max_lat - min_lat) > threshold

def build_overpass_query(poly_str):
    """
    Builds the Overpass API query string using a polygon string in "lat lon,lat lon,..." order.
    """
    return f"""
    [out:json][timeout:25];
    (
      node["addr:housenumber"](poly:"{poly_str}");
      way["addr:housenumber"](poly:"{poly_str}");
      relation["addr:housenumber"](poly:"{poly_str}");
    );
    out center;
    """

def parse_csv_file(uploaded_file, encoding="cp1250", delimiter=";"):
    """
    Wraps an uploaded file with a TextIOWrapper and returns a CSV DictReader.
    """
    try:
        decoded_file = io.TextIOWrapper(uploaded_file, encoding=encoding)
        reader = csv.DictReader(decoded_file, delimiter=delimiter)
        return reader
    except Exception as e:
        raise e

def customer_data_from_csv_row(row):
    """
    Given a CSV row (as a dict), returns a dictionary of customer data,
    including a Point object for the location. Returns None if lat/lon cannot be parsed.
    Expected CSV header columns:
        city, street_name, house_number, local, phone, email, lat, lon, (optionally note)
    """
    try:
        lat = float(row.get("lat", "").strip())
        lon = float(row.get("lon", "").strip())
    except (ValueError, AttributeError):
        return None
    point = Point(lon, lat)
    return {
        "location": point,
        "city": row.get("city", "").strip(),
        "street_name": row.get("street_name", "").strip(),
        "street_no": row.get("house_number", "").strip(),
        "local": row.get("local", "").strip(),
        "phone": row.get("phone", "").strip(),
        "email": row.get("email", "").strip(),
        "note": row.get("note", "").strip() if "note" in row else "",
        "status": "active",
    }
